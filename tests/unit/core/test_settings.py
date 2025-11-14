#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  8 20:11:15 2025

@author: vcsil

Testes para app.core.settings.

Garante que o módulo app.core.settings
  (1) leia as variáveis de ambiente corretas com casting de tipos,
  (2) rejeite timezones inválidos e
  (3) atualize .env + invalide/recarregue o cache quando set_settings(...) 
  for chamado
tudo em ambiente controlado de testes.
"""
from __future__ import annotations

from pydantic import ValidationError
from types import ModuleType
from importlib import reload
from pathlib import Path


import pytest


@pytest.fixture
def settings_module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Fornece o módulo de configurações com variáveis de ambiente controladas."""

    env_values = {
        "TIMEZONE_APP": "UTC",
        "TIMEZONE_BUSINESS": "America/Sao_Paulo",
        "POSTGRES_TZ": "America/Sao_Paulo",
        "BLING_CLIENT_ID": "cliente", 
        "BLING_CLIENT_SECRET": "segredo",
        "BLING_USUARIO": "usuario",
        "BLING_SENHA_USUARIO": "senha",
        "BLING_BASEURL": "https://bling.example/",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_CONTAINER_PORT": "5432",
        "POSTGRES_HOST_PORT": "5432",
        "POSTGRES_DB": "bling",
    }

    for key, value in env_values.items():
        monkeypatch.setenv(key, value)

    for optional_key in {
        "BLING_OAUTH_ACCESS_TOKEN",
        "BLING_OAUTH_EXPIRES_IN",
        "BLING_OAUTH_REFRESH_TOKEN",
        "BLING_OAUTH_SCOPE",
    }:
        monkeypatch.delenv(optional_key, raising=False)

    import app.core.settings as settings_module

    reload(settings_module)
    settings_module.get_settings.cache_clear()
    return settings_module


def test_get_settings_usa_variaveis_de_ambiente(settings_module) -> None:
    settings = settings_module.get_settings()

    assert settings.timezone_app == "UTC"
    assert settings.timezone_business == "America/Sao_Paulo"
    assert settings.postgres_tz == "America/Sao_Paulo"
    assert settings.bling_client_id == "cliente"
    assert settings.bling_client_secret == "segredo"
    assert settings.bling_usuario == "usuario"
    assert settings.bling_senha_usuario == "senha"
    assert str(settings.bling_baseurl) == "https://bling.example/"
    assert settings.postgres_user == "postgres"
    assert settings.postgres_password == "postgres"
    assert settings.postgres_host == "localhost"
    assert settings.postgres_container_port == 5432
    assert settings.postgres_host_port == 5432
    assert settings.postgres_db == "bling"


def test_validacao_no_blank_values(settings_module, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BLING_USUARIO", " ")
    settings_module.get_settings.cache_clear()

    with pytest.raises(ValidationError, match="Value cannot be blank or whitespace only"):
        settings_module.get_settings()


def test_validacao_min_length_bling_usuario(settings_module, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BLING_USUARIO", "")
    settings_module.get_settings.cache_clear()

    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        settings_module.get_settings()


@pytest.mark.parametrize("tz", ["UTC", "America/Sao_Paulo"])
def test_validacao_timezone_valido(settings_module, monkeypatch: pytest.MonkeyPatch, tz) -> None:
    monkeypatch.setenv("TIMEZONE_APP", tz)
    settings_module.get_settings.cache_clear()

    s = settings_module.get_settings()
    assert s.timezone_app == tz


def test_validacao_timezone_invalido(settings_module, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TIMEZONE_APP", "Terra/Plana")
    settings_module.get_settings.cache_clear()

    with pytest.raises(ValueError, match="Unknown timezone"):
        settings_module.get_settings()


def test_set_settings_atualiza_env_e_limpa_cache(settings_module, tmp_path: Path) -> None:
    settings_iniciais = settings_module.get_settings()
    caminho_env = tmp_path / ".env.test"
    caminho_env.touch()

    novos = settings_module.set_settings({"TIMEZONE_APP": "Europe/London"}, env_path=str(caminho_env))

    assert novos.timezone_app == "Europe/London"
    assert novos is not settings_iniciais
    assert caminho_env.read_text(encoding="utf-8").strip() == "TIMEZONE_APP=Europe/London"

    # A chamada seguinte deve refletir o valor atualizado mantido em cache
    atualizados = settings_module.get_settings()
    assert atualizados.timezone_app == "Europe/London"


def test_set_settings_sem_atualizacoes_retorna_mesma_instancia(settings_module) -> None:
    """Quando nenhum update é passado, set_settings deve apenas devolver o Settings atual."""
    settings_iniciais = settings_module.get_settings()

    resultado = settings_module.set_settings()  # sem updates, sem extra_updates

    assert resultado is settings_iniciais


def test_set_settings_usa_extra_updates_para_mesclar_configuracoes(
    settings_module,
    tmp_path: Path,
) -> None:
    """Garante que extra_updates (**kwargs) são mesclados em merged_updates e persistidos no .env."""
    settings_iniciais = settings_module.get_settings()
    caminho_env = tmp_path / ".env.extra"
    caminho_env.touch()

    # Não passamos 'updates', apenas extra_updates via kwargs
    novos = settings_module.set_settings(
        env_path=str(caminho_env),
        TIMEZONE_BUSINESS="Europe/Berlin",
    )

    # Como só usamos extra_updates, cobrimos o branch:
    # if extra_updates: merged_updates.update(extra_updates)
    assert novos.timezone_business == "Europe/Berlin"
    assert novos is not settings_iniciais

    # Confere se foi persistido corretamente no arquivo .env
    conteudo = caminho_env.read_text(encoding="utf-8").strip()
    assert conteudo == "TIMEZONE_BUSINESS=Europe/Berlin"

    # E se o cache foi recarregado com o valor novo
    atualizados = settings_module.get_settings()
    assert atualizados.timezone_business == "Europe/Berlin"


def test_set_settings_repassa_os_error_com_mensagem_amigavel(
    settings_module,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Se set_key levantar OSError, set_settings deve levantar um novo OSError com mensagem customizada."""
    caminho_env = tmp_path / ".env.error"

    def fake_set_key(*args, **kwargs):
        # Simula falha de escrita no arquivo .env
        raise OSError("Falha artificial de escrita")

    # Patching da função set_key importada dentro de app.core.settings
    monkeypatch.setattr(settings_module, "set_key", fake_set_key)

    expected_msg = f"Falha ao persistir configurações em {caminho_env}"

    with pytest.raises(OSError, match=expected_msg):
        settings_module.set_settings(
            {"TIMEZONE_APP": "Europe/London"},
            env_path=str(caminho_env),
        )
