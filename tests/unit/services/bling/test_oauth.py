#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 22:08:33 2025

@author: vcsil

Testes para app.services.bling.oauth.

Ele testa, ponta a ponta e sem rede real, o fluxo de OAuth do seu cliente do
Bling: serialização/expiração de token, renovação automática e forçada,
persistência em .env, e tratamento de falhas (erro de rede, HTTP 401 e JSON
inválido), usando pytest, monkeypatch, unittest.mock e importlib.reload
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from importlib import reload
from types import ModuleType
from typing import Any, Mapping

from unittest.mock import Mock
import requests
import pytest
import types
import sys

@pytest.fixture
def oauth_module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Fornece o módulo de OAuth com dependências recarregadas."""

    env_values = {
        "TIMEZONE_APP": "UTC",
        "TIMEZONE_BUSINESS": "America/Sao_Paulo",
        "POSTGRES_TZ": "America/Sao_Paulo",
        "BLING_CLIENT_ID": "cliente",
        "BLING_CLIENT_SECRET": "segredo",
        "BLING_USUARIO": "usuario",
        "BLING_SENHA_USUARIO": "senha",
        "BLING_BASEURL": "https://bling.example",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_CONTAINER_PORT": "5432",
        "POSTGRES_HOST_PORT": "5432",
        "POSTGRES_DB": "bling",
        "BLING_OAUTH_REFRESH_TOKEN": "token_atual",
    }

    for key, value in env_values.items():
        monkeypatch.setenv(key, value)

    for optional in {
        "BLING_OAUTH_ACCESS_TOKEN",
        "BLING_OAUTH_EXPIRES_IN",
        "BLING_OAUTH_REFRESH_TOKEN",
        "BLING_OAUTH_SCOPE",
        "BLING_OAUTH_HOURS_EXPIRATION",
    }:
        monkeypatch.delenv(optional, raising=False)

    import app.core.settings as settings_module

    # isolar do .env real
    settings_module.ENV_PATH = "nonexistent.env"
    settings_module.Settings.model_config["env_file"] = "nonexistent.env"

    reload(settings_module)
    settings_module.get_settings.cache_clear()

    import app.core.timeutil as timeutil_module

    reload(timeutil_module)

    import app.services.bling.oauth as oauth

    reload(oauth)
    return oauth


@pytest.fixture
def settings(oauth_module: ModuleType) -> Any:
    return oauth_module.get_settings()


def test_oauth_token_serializa_e_calcula_expiracao(
    oauth_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Simula um token criado em 2024, com duração de 1h e verifica se os dados 
    continuam certos e se o calculo da expiração está correta.
    """
    # Simula comportamento
    instante = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(oauth_module, "time_now", lambda: instante)

    token = oauth_module.OAuthToken(
        access_token="abc123",
        expires_in=3600,
        token_type="Bearer",
        scope="perfil",
        refresh_token="refresh123",
        obtained_at=instante,
    )

    esperado = oauth_module.time_to_business(
        instante + timedelta(seconds=token.expires_in)
    )
    assert token.expires_at == esperado

    serializado = token.model_dump(by_alias=True)
    assert serializado["access_token"] == "abc123"
    assert serializado["expires_in"] == 3600

    monkeypatch.setattr(oauth_module, "time_now", lambda: instante + timedelta(seconds=3599))
    assert token.is_expired(leeway=0) is False

    monkeypatch.setattr(oauth_module, "time_now", lambda: instante + timedelta(seconds=3600))
    assert token.is_expired(leeway=0) is True


def test_get_token_renova_automaticamente_quando_expira(
    oauth_module: ModuleType,
    settings: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Simula um token expirado e o fluxo para atualizar
    """
    cliente = oauth_module.BlingOAuthClient(settings=settings)

    instante = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    expirado = oauth_module.OAuthToken(
        access_token="antigo",
        expires_in=10,
        token_type="Bearer",
        refresh_token="token_atual",
        obtained_at=instante,
    )
    cliente._token = expirado

    novo_token = oauth_module.OAuthToken(
        access_token="novo",
        expires_in=3600,
        token_type="Bearer",
        refresh_token="token_atualizado",
        obtained_at=instante + timedelta(seconds=20),
    )

    chamada = {"executada": 0}

    def _falso_refresh(*, save_to_env: bool = True) -> oauth_module.OAuthToken:
        chamada["executada"] += 1
        return novo_token

    monkeypatch.setattr(cliente, "refresh_access_token", _falso_refresh)
    monkeypatch.setattr(
        oauth_module,
        "time_now",
        lambda: instante + timedelta(seconds=600),
    )

    resultado = cliente.get_token()

    assert resultado is novo_token
    assert chamada["executada"] == 1
    assert cliente._token is novo_token

    resultado_forcado = cliente.get_token(force_refresh=True)
    assert resultado_forcado is novo_token
    assert chamada["executada"] == 2


def test_refresh_access_token_sem_refresh_token_dispara_erro(
    oauth_module: ModuleType, settings: Any
) -> None:
    """
    Verifica se o tratamento de erro para client sem refresh token está certo.
    """
    cliente = oauth_module.BlingOAuthClient(settings=settings)
    cliente._refresh_token = None

    with pytest.raises(oauth_module.BlingOAuthError, match="Refresh token inexistente"):
        cliente.refresh_access_token()


def test_refresh_access_token_persiste_token_quando_configurado(
    oauth_module: ModuleType,
    settings: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Testa se o token é persistido quando ele é requisitado."""
    cliente = oauth_module.BlingOAuthClient(settings=settings)

    token_atualizado = oauth_module.OAuthToken(
        access_token="novo",
        expires_in=1800,
        token_type="Bearer",
        scope="perfil",
        refresh_token="novo_refresh",
        obtained_at=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
    )

    monkeypatch.setattr(cliente, "_request_token", lambda payload: token_atualizado)

    capturado: dict[str, Mapping[str, str | None]] = {}

    def _falso_set_settings(
        valores: Mapping[str, str | None],
        *,
        env_path: str | None = None,
    ) -> Any:
        capturado["dados"] = valores
        return settings

    monkeypatch.setattr(oauth_module, "set_settings", _falso_set_settings)

    resultado = cliente.refresh_access_token(save_to_env=False)

    assert resultado is token_atualizado
    assert capturado == {}
    assert cliente._refresh_token == "novo_refresh"


def test_refresh_access_token_persiste_token_quando_configurado_persite(
    oauth_module: ModuleType,
    settings: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Testa atualização do token e se ele é persistido."""
    cliente = oauth_module.BlingOAuthClient(settings=settings)

    token_atualizado = oauth_module.OAuthToken(
        access_token="novo",
        expires_in=1800,
        token_type="Bearer",
        scope="perfil",
        refresh_token="novo_refresh",
        obtained_at=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
    )

    monkeypatch.setattr(cliente, "_request_token", lambda payload: token_atualizado)

    capturado: dict[str, Mapping[str, str | None]] = {}

    def _falso_set_settings(
        valores: Mapping[str, str | None],
        *,
        env_path: str | None = None,
    ) -> Any:
        capturado["dados"] = valores
        return settings

    monkeypatch.setattr(oauth_module, "set_settings", _falso_set_settings)

    resultado = cliente.refresh_access_token(save_to_env=True)

    assert resultado is token_atualizado
    assert capturado["dados"][cliente.ENV_ACCESS_TOKEN_KEY] == "novo"
    assert capturado["dados"][cliente.ENV_REFRESH_TOKEN_KEY] == "novo_refresh"
    assert cliente._refresh_token == "novo_refresh"


def test_request_token_trata_erros_de_rede(
    oauth_module: ModuleType, settings: Any
) -> None:
    """Verifica se trata erro ao tentar solicitar token."""
    sessao = Mock(spec=requests.Session)
    sessao.post.side_effect = requests.RequestException("falhou")

    cliente = oauth_module.BlingOAuthClient(settings=settings, session=sessao)

    with pytest.raises(oauth_module.BlingOAuthError, match="Falha ao se comunicar"):
        cliente._request_token({"grant_type": "refresh_token"})


def test_request_token_com_status_de_erro_gera_excecao(
    oauth_module: ModuleType, settings: Any
) -> None:
    """Simula o tratamento de uma requisição feita errada."""
    class RespostaErro:
        status_code = 401
        text = "{\"erro\": \"invalid_client\"}"

        def json(self) -> Mapping[str, Any]:
            return {"erro": "invalid_client"}

    sessao = Mock(spec=requests.Session)
    sessao.post.return_value = RespostaErro()

    cliente = oauth_module.BlingOAuthClient(settings=settings, session=sessao)

    with pytest.raises(oauth_module.BlingOAuthError, match="status 401"):
        cliente._request_token({"grant_type": "refresh_token"})


def test_request_token_rejeita_json_invalido(
    oauth_module: ModuleType, settings: Any
) -> None:
    """Trata erro de quando o token retornado não é um json."""
    class RespostaFalsa:
        status_code = 200
        text = "<<<não é json>>>"

        def json(self) -> Mapping[str, Any]:
            raise ValueError("inválido")

    sessao = Mock(spec=requests.Session)
    sessao.post.return_value = RespostaFalsa()

    cliente = oauth_module.BlingOAuthClient(settings=settings, session=sessao)

    with pytest.raises(oauth_module.BlingOAuthError, match="Resposta inesperada"):
        cliente._request_token({"grant_type": "refresh_token"})


def test_exchange_code_for_token_atualiza_refresh(
    oauth_module: ModuleType,
    settings: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica se o access token está sendo trocado por auth token."""
    cliente = oauth_module.BlingOAuthClient(settings=settings)
    cliente._refresh_token = "antigo_refresh"

    token_novo = oauth_module.OAuthToken(
        access_token="novo",
        expires_in=1800,
        token_type="Bearer",
        refresh_token="refresh_trocado",
        obtained_at=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
    )

    monkeypatch.setattr(cliente, "_request_token", lambda payload: token_novo)
    persistido = {"executado": False}

    def _falso_persistir(token: oauth_module.OAuthToken) -> None:
        persistido["executado"] = True

    monkeypatch.setattr(cliente, "_persist_token", _falso_persistir)

    resultado = cliente.exchange_code_for_token("codigo", save_to_env=False)

    assert resultado is token_novo
    assert cliente._refresh_token == "refresh_trocado"
    assert persistido["executado"] is False


def test_exchange_code_for_token_atualiza_refresh_persiste(
    oauth_module: ModuleType,
    settings: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica se o access token está sendo trocado por auth token."""
    cliente = oauth_module.BlingOAuthClient(settings=settings)
    cliente._refresh_token = "antigo_refresh"

    token_novo = oauth_module.OAuthToken(
        access_token="novo",
        expires_in=1800,
        token_type="Bearer",
        refresh_token="refresh_trocado",
        obtained_at=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
    )

    monkeypatch.setattr(cliente, "_request_token", lambda payload: token_novo)
    persistido = {"executado": False}

    def _falso_persistir(token: oauth_module.OAuthToken) -> None:
        persistido["executado"] = True

    monkeypatch.setattr(cliente, "_persist_token", _falso_persistir)

    resultado = cliente.exchange_code_for_token("codigo", save_to_env=True)

    assert resultado is token_novo
    assert cliente._refresh_token == "refresh_trocado"
    assert persistido["executado"] is True


def test_build_authorization_url(
    oauth_module: ModuleType,
    settings: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Testa a criação de url."""
    cliente = oauth_module.BlingOAuthClient(settings=settings)
    url = cliente.build_authorization_url(state="vasco")

    url_base = url.split("?")[0]
    url_params = url.split("?")[1]

    params = []
    for param in url_params.split("&"):
        params += [param]

    assert url_base == str(settings.bling_baseurl) + "oauth/authorize"
    assert params[0] == "response_type=code"
    assert params[1] == "client_id=" + str(settings.bling_client_id)
    assert params[2] == "state=vasco"


def test_request_token_sucesso_retorna_token_valido(
    oauth_module: ModuleType,
    settings: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Caminho de sucesso de _request_token: status 200 e JSON válido.
    Garante que:
      - o JSON é convertido em dict (linha 289),
      - 'obtained_at' é preenchido com time_now() (linha 293),
      - OAuthToken.model_validate é chamado e um token é retornado (295–296).
    """
    instante = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    # Deixa time_now determinístico para podermos checar o obtained_at
    monkeypatch.setattr(oauth_module, "time_now", lambda: instante)

    class RespostaSucesso:
        status_code = 200
        text = '{"access_token": "abc123", "expires_in": 3600, "token_type": "Bearer"}'

        def json(self) -> Mapping[str, Any]:
            # _safe_json vai retornar esse dict e cair no ramo isinstance(data, Mapping)
            return {
                "access_token": "abc123",
                "expires_in": 3600,
                "token_type": "Bearer",
            }

    sessao = Mock(spec=requests.Session)
    sessao.post.return_value = RespostaSucesso()

    cliente = oauth_module.BlingOAuthClient(settings=settings, session=sessao)

    token = cliente._request_token({"grant_type": "refresh_token"})

    # Asserções para garantir que o fluxo feliz completou
    assert isinstance(token, oauth_module.OAuthToken)
    assert token.access_token == "abc123"
    assert token.expires_in == 3600
    assert token.token_type == "Bearer"
    # Confere que o obtained_at veio do time_now() (linha 293)
    assert token.obtained_at == instante


# Stub do Selenium aqui pq ele só é utilizado aqui.
def _stub_selenium_for_authorize_with_browser(
    monkeypatch: pytest.MonkeyPatch,
    *,
    code_in_callback: str | None = "codigo123",
    sem_botao_autorizar: bool = False,
):
    """
    Injeta módulos falsos de selenium e webdriver_manager.chrome em sys.modules,
    para que authorize_with_browser funcione sem depender de Chrome real.

    - code_in_callback: código que aparecerá na query string da current_url
    - sem_botao_autorizar: se True, simula ausência do botão "Autorizar"
      (dispara NoSuchElementException e cai no branch de sessão reutilizada)
    """

    # Exceção que o código espera capturar
    class NoSuchElementException(Exception):
        pass

    # selenium.common.exceptions
    m_exceptions = types.ModuleType("selenium.common.exceptions")
    m_exceptions.NoSuchElementException = NoSuchElementException
    monkeypatch.setitem(sys.modules, "selenium.common.exceptions", m_exceptions)

    # selenium.webdriver.chrome.service.Service
    m_service = types.ModuleType("selenium.webdriver.chrome.service")

    class Service:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    m_service.Service = Service
    monkeypatch.setitem(sys.modules, "selenium.webdriver.chrome.service", m_service)

    # selenium.webdriver.common.by.By
    m_by = types.ModuleType("selenium.webdriver.common.by")

    class By:
        XPATH = "XPATH"

    m_by.By = By
    monkeypatch.setitem(sys.modules, "selenium.webdriver.common.by", m_by)

    # Elemento genérico com send_keys / click
    class DummyElement:
        def __init__(self, calls: list[tuple]):
            self._calls = calls

        def send_keys(self, value: str) -> None:
            self._calls.append(("send_keys", value))

        def click(self) -> None:
            self._calls.append(("click",))

    # WebDriver falso
    class DummyDriver:
        def __init__(self, service=None, options=None):
            self.service = service
            self.options = options
            self.calls: list[tuple] = []

            if code_in_callback is None:
                # caso de erro: nenhuma query "code"
                self.current_url = "https://bling.example/oauth/callback?erro=access_denied"
            else:
                self.current_url = f"https://bling.example/oauth/callback?code={code_in_callback}"

        def implicitly_wait(self, seconds: int) -> None:
            self.calls.append(("implicitly_wait", seconds))

        def get(self, url: str) -> None:
            self.calls.append(("get", url))

        def find_element(self, by, value: str) -> DummyElement:
            self.calls.append(("find_element", by, value))
            # Quando procurar o botão de autorizar e pedimos para simular
            # sessão reutilizada, disparamos NoSuchElementException
            if sem_botao_autorizar and "form/button[2]" in value:
                raise NoSuchElementException("botão de autorizar não encontrado")
            return DummyElement(self.calls)

        def quit(self) -> None:
            self.calls.append(("quit",))

    # selenium.webdriver.Chrome
    m_webdriver = types.ModuleType("selenium.webdriver")
    m_webdriver.Chrome = DummyDriver
    monkeypatch.setitem(sys.modules, "selenium.webdriver", m_webdriver)

    # pacote selenium (usado por "from selenium import webdriver")
    m_selenium = types.ModuleType("selenium")
    m_selenium.webdriver = m_webdriver
    monkeypatch.setitem(sys.modules, "selenium", m_selenium)

    # webdriver_manager.chrome.ChromeDriverManager
    m_wm = types.ModuleType("webdriver_manager.chrome")

    class ChromeDriverManager:
        def install(self) -> str:
            return "/fake/chromedriver"

    m_wm.ChromeDriverManager = ChromeDriverManager
    monkeypatch.setitem(sys.modules, "webdriver_manager.chrome", m_wm)

    return DummyDriver


def test_authorize_with_browser_fluxo_normal(
    oauth_module: ModuleType,
    settings: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Fluxo normal do authorize_with_browser: botão Autorizar existe,
    URL final contém ?code=..., e o código é trocado por token.
    """
    _stub_selenium_for_authorize_with_browser(
        monkeypatch,
        code_in_callback="codigo123",
        sem_botao_autorizar=False,
    )

    # Evita precisar de Options real do selenium
    def fake_build_chrome_options(*, headless: bool) -> Any:
        return {"headless": headless}

    monkeypatch.setattr(
        oauth_module.BlingOAuthClient,
        "_build_chrome_options",
        staticmethod(fake_build_chrome_options),
    )

    cliente = oauth_module.BlingOAuthClient(settings=settings)

    capturado: dict[str, Any] = {}

    def fake_exchange_code_for_token(code: str, *, save_to_env: bool) -> Any:
        capturado["code"] = code
        capturado["save_to_env"] = save_to_env
        # retorna um token válido p/ não depender de rede
        return oauth_module.OAuthToken(
            access_token="token_xyz",
            expires_in=3600,
            token_type="Bearer",
            refresh_token="refresh_xyz",
            obtained_at=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
        )

    monkeypatch.setattr(
        cliente,
        "exchange_code_for_token",
        fake_exchange_code_for_token,
    )

    token = cliente.authorize_with_browser(
        state="estado_teste",
        headless=True,
        save_to_env=False,
    )

    # Verifica que o fluxo completou
    assert isinstance(token, oauth_module.OAuthToken)
    assert token.access_token == "token_xyz"
    # Confere que o código veio da URL simulada
    assert capturado["code"] == "codigo123"
    # Confere propagação do parâmetro save_to_env
    assert capturado["save_to_env"] is False


def test_authorize_with_browser_sessao_reutilizada_quando_nao_ha_botao_autorizar(
    oauth_module: ModuleType,
    settings: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Se o botão Autorizar não é encontrado, o código deve tratar
    NoSuchElementException e seguir normalmente (sessão reutilizada).
    """
    _stub_selenium_for_authorize_with_browser(
        monkeypatch,
        code_in_callback="codigo456",
        sem_botao_autorizar=True,  # força cair no except
    )

    def fake_build_chrome_options(*, headless: bool) -> Any:
        return {"headless": headless}

    monkeypatch.setattr(
        oauth_module.BlingOAuthClient,
        "_build_chrome_options",
        staticmethod(fake_build_chrome_options),
    )

    cliente = oauth_module.BlingOAuthClient(settings=settings)

    capturado: dict[str, Any] = {}

    def fake_exchange_code_for_token(code: str, *, save_to_env: bool) -> Any:
        capturado["code"] = code
        capturado["save_to_env"] = save_to_env
        return oauth_module.OAuthToken(
            access_token="token_reuso",
            expires_in=1800,
            token_type="Bearer",
            refresh_token="refresh_reuso",
            obtained_at=datetime(2024, 1, 1, 13, 0, tzinfo=timezone.utc),
        )

    monkeypatch.setattr(
        cliente,
        "exchange_code_for_token",
        fake_exchange_code_for_token,
    )

    token = cliente.authorize_with_browser(
        state="estado_teste",
        headless=False,
        save_to_env=True,
    )

    assert isinstance(token, oauth_module.OAuthToken)
    assert token.access_token == "token_reuso"
    assert capturado["code"] == "codigo456"
    assert capturado["save_to_env"] is True


def test_authorize_with_browser_sem_codigo_na_url_dispara_erro(
    oauth_module: ModuleType,
    settings: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Quando a URL final não contém o parâmetro 'code', deve ser levantado
    BlingOAuthError.
    """
    _stub_selenium_for_authorize_with_browser(
        monkeypatch,
        code_in_callback=None,        # gera URL sem ?code=
        sem_botao_autorizar=False,
    )

    def fake_build_chrome_options(*, headless: bool) -> Any:
        return {"headless": headless}

    monkeypatch.setattr(
        oauth_module.BlingOAuthClient,
        "_build_chrome_options",
        staticmethod(fake_build_chrome_options),
    )

    cliente = oauth_module.BlingOAuthClient(settings=settings)

    # exchange_code_for_token não deve nem ser chamado
    chamado = {"executado": False}

    def fake_exchange_code_for_token(code: str, *, save_to_env: bool) -> Any:
        chamado["executado"] = True

    monkeypatch.setattr(
        cliente,
        "exchange_code_for_token",
        fake_exchange_code_for_token,
    )

    with pytest.raises(
        oauth_module.BlingOAuthError,
        match="Código de autorização não encontrado na URL de retorno",
    ):
        cliente.authorize_with_browser(state="estado_teste")

    assert chamado["executado"] is False
