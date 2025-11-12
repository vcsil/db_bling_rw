"""Testes para app.services.bling.oauth."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from importlib import reload
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping
import sys

import pytest
import requests
from unittest.mock import Mock


def _ensure_src_in_path() -> None:
    caminho_teste = Path(__file__).resolve()
    for parent in caminho_teste.parents:
        candidato = parent / "src"
        if candidato.exists():
            if str(candidato) not in sys.path:
                sys.path.insert(0, str(candidato))
            return
    raise RuntimeError("Diretório 'src' não encontrado na hierarquia de testes")


@pytest.fixture
def oauth_module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Fornece o módulo de OAuth com dependências recarregadas."""

    _ensure_src_in_path()
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
        "BLING_OAUTH_SCOPE",
    }:
        monkeypatch.delenv(optional, raising=False)

    import app.core.settings as settings_module

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
    cliente = oauth_module.BlingOAuthClient(settings=settings)
    cliente._refresh_token = None

    with pytest.raises(oauth_module.BlingOAuthError, match="Refresh token inexistente"):
        cliente.refresh_access_token()


def test_refresh_access_token_persiste_token_quando_configurado(
    oauth_module: ModuleType,
    settings: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
    sessao = Mock(spec=requests.Session)
    sessao.post.side_effect = requests.RequestException("falhou")

    cliente = oauth_module.BlingOAuthClient(settings=settings, session=sessao)

    with pytest.raises(oauth_module.BlingOAuthError, match="Falha ao se comunicar"):
        cliente._request_token({"grant_type": "refresh_token"})


def test_request_token_com_status_de_erro_gera_excecao(
    oauth_module: ModuleType, settings: Any
) -> None:
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
