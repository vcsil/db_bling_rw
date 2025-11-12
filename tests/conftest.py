"""Configurações globais de testes."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from types import ModuleType
from typing import IO, Iterator

import pytest


def _stub_dotenv_module() -> None:
    if "dotenv" in sys.modules:
        return

    module = ModuleType("dotenv")

    def find_dotenv(*, usecwd: bool = False) -> str:
        return ""

    def load_dotenv(*, dotenv_path: str | None = None, override: bool = False) -> bool:
        if not dotenv_path:
            return False
        caminho = Path(dotenv_path)
        if not caminho.exists():
            return False
        alterado = False
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            if not linha or linha.lstrip().startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            if override or chave not in os.environ:
                os.environ[chave] = valor
                alterado = True
        return alterado

    def set_key(dotenv_path: str, key: str, value: str) -> tuple[str, str, bool]:
        caminho = Path(dotenv_path)
        pares: dict[str, str] = {}
        if caminho.exists():
            for linha in caminho.read_text(encoding="utf-8").splitlines():
                if not linha or linha.lstrip().startswith("#") or "=" not in linha:
                    continue
                atual_chave, atual_valor = linha.split("=", 1)
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
            if not linha or linha.lstrip().startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            pares[chave] = valor
        return pares

    module.find_dotenv = find_dotenv
    module.load_dotenv = load_dotenv
    module.set_key = set_key
    module.dotenv_values = dotenv_values
    sys.modules["dotenv"] = module


@pytest.fixture(autouse=True)
def _patch_dotenv() -> Iterator[None]:
    _stub_dotenv_module()
    yield
