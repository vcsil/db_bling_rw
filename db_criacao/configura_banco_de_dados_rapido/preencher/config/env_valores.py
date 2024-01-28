#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 09:19:10 2023.

@author: vcsil
"""

from bling_api_v3_oauth.BlingV3 import oauth_blingV3

from dotenv import dotenv_values, get_key
from typing import Dict, Optional
from pathlib import Path
import logging

log = logging.getLogger(__name__)

# =-=-=-=-=-=-=-=-=-=-=-=- Carregando chaves de acesso =-=-=-=-=-=-=-=-=-=-=-=-


class EnvValores():
    """Lida com os arquivo env do projeto."""

    def __init__(self) -> None:
        self.env_path = ".env"

    def pega_variaveis_ambiente(self) -> Dict[str, Optional[str]]:
        """
        Pega os valores das variáveis de ambiente.

        Parameters
        ----------
        dotenv_path : Union[str, os.PathLike, None], optional
            DESCRIPTION. The default is None.

        Returns
        -------
        Dict[str, Optional[str]]
            Todas variáveis do .env do projeto.

        """
        env = dotenv_values(dotenv_path=self.env_path)
        log.info('Fim pegar variáveis de ambiente geral')
        return env

    def env_api(self) -> Dict[str, str]:
        """Filtra as variáveis usadas na conexão com a API."""
        log.info("Começa a pegar variáveis referentes a API")
        self._check_credencial_api()

        env = self.pega_variaveis_ambiente()
        env_da_api = {chave: valor for chave, valor in env.items()
                      if 'OAUTH' in chave}
        log.info('Fim pegar variáveis de ambiente da api')
        return env_da_api

    def _check_credencial_api(self):
        """Verifica se o access token existe no .env, se não tiver solicita."""
        log.info("Verifica se existe access token no .env, ou solicita novo")
        OAUTH_ACCESS_TOKEN = get_key(dotenv_path=self.env_path,
                                     key_to_get="OAUTH_ACCESS_TOKEN")

        if not (OAUTH_ACCESS_TOKEN):
            # Solicita novas credenciais de acesso e salva no arquivo .env
            log.info("Solicina novas credenciais de acesso")
            oauth_blingV3(save_env=True, save_txt=False)

    def env_db(self) -> Dict[str, str]:
        """Filtra as variáveis usadas na conexão com o banco de dados."""
        log.info("Começa a pegar variáveis referentes a API")
        self._check_credencial_api()

        env = self.pega_variaveis_ambiente()
        env_do_db = {chave: valor for chave, valor in env.items()
                     if 'POSTGRES' in chave}
        log.info('Fim pegar variáveis de ambiente do db')
        return env_do_db


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-=-=-
