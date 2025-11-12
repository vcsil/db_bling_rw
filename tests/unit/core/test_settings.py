"""Testes para app.core.settings."""
from __future__ import annotations

from importlib import reload
from pathlib import Path
from types import ModuleType
import sys

import pytest


def _ensure_src_in_path() -> None:
    raiz = Path(__file__).resolve().parents[3] / "src"
    if str(raiz) not in sys.path:
        sys.path.insert(0, str(raiz))


@pytest.fixture
def settings_module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Fornece o módulo de configurações com variáveis de ambiente controladas."""

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
    assert settings.bling_client_id == "cliente"
    assert settings.postgres_container_port == 5432


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
    conteudo_env = caminho_env.read_text(encoding="utf-8").strip()
    assert conteudo_env in {
        "TIMEZONE_APP=Europe/London",
        "TIMEZONE_APP='Europe/London'",
        'TIMEZONE_APP="Europe/London"',
    }

    # A chamada seguinte deve refletir o valor atualizado mantido em cache
    atualizados = settings_module.get_settings()
    assert atualizados.timezone_app == "Europe/London"
