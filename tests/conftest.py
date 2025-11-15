#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  8 19:39:16 2025

@author: vcsil

Configurações globais de testes.

Cria um “clone mínimo” do pacote python-dotenv, requests
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from types import ModuleType
from typing import IO, Iterator

import pytest


def _ensure_src_in_path() -> None:
    caminho_teste = Path(__file__).resolve()
    for idx, parent in enumerate(caminho_teste.parents):

        if idx > 1:
            raise RuntimeError("Diretório 'src' não encontrado na hierarquia de testes")
            
        candidato = parent / "src"
        if candidato.exists():
            if str(candidato) not in sys.path:
                sys.path.insert(0, str(candidato))
            return


def _stub_dotenv_module() -> None:
    if "dotenv" in sys.modules:
        return

    module = ModuleType("dotenv")

    def find_dotenv(*, usecwd: bool = False) -> str:
        return ""

    def _parse_line(linha: str) -> tuple[str, str] | None:
        if not linha or linha.lstrip().startswith("#") or "=" not in linha:
            return None

        chave, valor = linha.split("=", 1)
        chave = chave.strip()
        valor = valor.strip()

        # remove aspas simétricas tipo 'valor' ou "valor"
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in {"'", '"'}:
            valor = valor[1:-1]

        return chave, valor

    def load_dotenv(*, dotenv_path: str | None = None, override: bool = False) -> bool:
        if not dotenv_path:
            return False

        caminho = Path(dotenv_path)
        if not caminho.exists():
            return False

        alterado = False
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            parsed = _parse_line(linha)
            if not parsed:
                continue
            chave, valor = parsed
            if override or chave not in os.environ:
                os.environ[chave] = valor
                alterado = True
        return alterado

    def set_key(dotenv_path: str, key: str, value: str, **kwargs) -> tuple[str, str, bool]:
        caminho = Path(dotenv_path)

        pares: dict[str, str] = {}
        if caminho.exists():
            for linha in caminho.read_text(encoding="utf-8").splitlines():
                parsed = _parse_line(linha)
                if not parsed:
                    continue
                atual_chave, atual_valor = parsed
                pares[atual_chave] = atual_valor

        pares[key] = value
        conteudo = "\n".join(f"{k}={v}" for k, v in pares.items())
        caminho.write_text(conteudo, encoding="utf-8")
        return key, value, True

    def dotenv_values(
        dotenv_path: str | os.PathLike[str] | None = None,
        stream: IO[str] | None = None,
        encoding: str | None = "utf-8",
        *,
        verbose: bool = False,
        interpolate: bool = False,
    ) -> dict[str, str]:
        if stream is not None:
            linhas = stream.read().splitlines()
        elif dotenv_path:
            caminho = Path(dotenv_path)
            if not caminho.exists():
                return {}
            linhas = caminho.read_text(encoding=encoding or "utf-8").splitlines()
        else:
            return {}

        pares: dict[str, str] = {}
        for linha in linhas:
            parsed = _parse_line(linha)
            if not parsed:
                continue
            chave, valor = parsed
            pares[chave] = valor
        return pares

    module.find_dotenv = find_dotenv
    module.load_dotenv = load_dotenv
    module.set_key = set_key
    module.dotenv_values = dotenv_values
    sys.modules["dotenv"] = module


def _stub_requests_module() -> None:
    if "requests" in sys.modules:
        return

    module = ModuleType("requests")

    class RequestException(Exception):
        """Exceção base para falhas simuladas do requests."""

    class Session:
        """Sessão HTTP mínima para ser usada como spec em mocks."""

        def post(self, *args: object, **kwargs: object) -> object:  # pragma: no cover
            raise NotImplementedError

        def request(self, *args: object, **kwargs: object) -> object:  # pragma: no cover
            raise NotImplementedError

    auth_module = ModuleType("requests.auth")

    class HTTPBasicAuth:  # pragma: no cover - comportamento trivial
        def __init__(self, username: str, password: str) -> None:
            self.username = username
            self.password = password

    auth_module.HTTPBasicAuth = HTTPBasicAuth

    class Response:
        status_code = 200
        text = ""

        def json(self) -> object:  # pragma: no cover - comportamento trivial
            return {}

    module.RequestException = RequestException
    module.Session = Session
    module.Response = Response
    module.auth = auth_module

    sys.modules["requests"] = module
    sys.modules["requests.auth"] = auth_module


@pytest.fixture(autouse=True, scope="session")
def _patch_dotenv() -> Iterator[None]:
    _stub_dotenv_module()
    yield

_stub_dotenv_module()
_stub_requests_module()
_ensure_src_in_path()
