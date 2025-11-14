#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 15:37:56 2025

@author: vcsil

Testes para app.core.timeutil.

Valida que o módulo app.core.timeutil
  (i) devolve “agora” em UTC com tzinfo correto,
  (ii) converte corretamente entre UTC e o fuso “business” das suas settings,
  (iii) rejeita datetimes ingênuos (sem tzinfo), e
  (iv) formata ISO-8601 com sufixo Z
"""
from __future__ import annotations

from datetime import datetime, timezone
from importlib import reload
from types import ModuleType

import pytest
from zoneinfo import ZoneInfo

@pytest.fixture
def timeutil_module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Carrega o módulo de utilitários de tempo com ambientes controlados."""

    monkeypatch.setenv("TIMEZONE_APP", "UTC")
    monkeypatch.setenv("TIMEZONE_BUSINESS", "America/Sao_Paulo")
    monkeypatch.setenv("POSTGRES_TZ", "America/Sao_Paulo")
    monkeypatch.setenv("BLING_CLIENT_ID", "cliente")
    monkeypatch.setenv("BLING_CLIENT_SECRET", "segredo")
    monkeypatch.setenv("BLING_USUARIO", "usuario")
    monkeypatch.setenv("BLING_SENHA_USUARIO", "senha")
    monkeypatch.setenv("BLING_BASEURL", "https://bling.example")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "postgres")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_CONTAINER_PORT", "5432")
    monkeypatch.setenv("POSTGRES_HOST_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "bling")

    import app.core.settings as settings_module

    reload(settings_module)
    settings_module.get_settings.cache_clear()

    import app.core.timeutil as timeutil

    reload(timeutil)
    return timeutil


def test_time_now_retorna_em_utc(timeutil_module: ModuleType) -> None:
    agora = timeutil_module.time_now()

    assert agora.tzinfo is timezone.utc


def test_time_to_utc_converte_zoneado(timeutil_module: ModuleType) -> None:
    zona_sp = ZoneInfo("America/Sao_Paulo")
    dt = datetime(2024, 5, 10, 12, 30, tzinfo=zona_sp)

    convertido = timeutil_module.time_to_utc(dt)

    hr_utc = dt.hour + 3 
    hr_utc = hr_utc if hr_utc < 24 else hr_utc - 24

    assert convertido.tzinfo is timezone.utc
    assert convertido.hour == hr_utc  # UTC é +3 em maio para São Paulo


def test_time_to_utc_exige_tzinfo(timeutil_module: ModuleType) -> None:
    dt_naive = datetime(2024, 5, 10, 12, 30)

    with pytest.raises(ValueError):
        timeutil_module.time_to_utc(dt_naive)


def test_time_to_business_converte_para_fuso(timeutil_module: ModuleType) -> None:
    dt_utc = datetime(2024, 5, 10, 15, 30, tzinfo=timezone.utc)

    convertido = timeutil_module.time_to_business(dt_utc)

    hr_utc = dt_utc.hour - 3
    hr_utc = hr_utc if hr_utc > 0 else hr_utc + 24

    assert convertido.tzinfo == ZoneInfo("America/Sao_Paulo")
    assert convertido.hour == hr_utc


def test_iso_z_formata_com_sufixo_z(timeutil_module: ModuleType) -> None:
    dt = datetime(2024, 5, 10, 12, 30, tzinfo=ZoneInfo("America/Sao_Paulo"))

    resultado = timeutil_module.iso_z(dt)

    assert resultado.endswith("Z")
    assert "T" in resultado


def test_time_to_business_exige_tzinfo(timeutil_module: ModuleType) -> None:
    dt_naive = datetime(2024, 5, 10, 12, 30)

    # Deve levantar o mesmo ValueError da linha 29 de timeutil.py
    with pytest.raises(ValueError, match="datetime naïve"):
        timeutil_module.time_to_business(dt_naive)

