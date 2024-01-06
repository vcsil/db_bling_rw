#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 10:14:53 2023.

@author: vcsil
"""
from bling_api_v3_oauth.BlingV3 import oauth_refresh_blingV3
from config.erros.erros import UnauthorizedError
from config.env_valores import EnvValores

from requests.exceptions import ConnectionError, RequestException
from typing import Dict, Optional
import requests
import logging
import random
import time

log = logging.getLogger(__name__)

# =-=-=-=-=-=-=-=-=-=-=-=-= Configurando acesso a API =-=-=-=-=-=-=-=-=-=-=-=-=


class ConectaAPI():
    """Controla conexão com API."""

    def __init__(self):
        self._env = EnvValores().env_api()
        self.rota = self._env['OAUTH_BASEURL']
        self.header = self.cria_header_http(self._env['OAUTH_ACCESS_TOKEN'])

    def cria_header_http(self, access_token: str) -> Dict[str, str]:
        """
        Cria header utilizado nas requisições da API V3 Bling.

        Parameters
        ----------
        access_token : str
            Token de acesso gerado pelo bling.

        Returns
        -------
        Dict[str]
            Header com 'Accept' e 'Authorization'.

        """
        header = {
          'Accept': 'application/json',
          'Authorization': f"Bearer {access_token}"
        }
        return header

    def _atualiza_token(self, refresh_token: str) -> Dict[str, Optional[str]]:
        """
        Gera um novo token de acesso a partir do refresh token.

        Atualiza header e .env

        Parameters
        ----------
        refresh_token : str
            Gerado na criação de credenciais, fica dentro do .env.

        Returns
        -------
        Dict[str]
            Retorna o header da requisição.

        """
        log.info("Inicia")
        # Faz requisição de novas credenciais
        log.info("Solicita refresh token")
        oauth_refresh_blingV3(
            refresh_token=refresh_token,
            save_env=True,
            save_txt=False
        )
        # Atualiza a variável env com as novas variáveis de ambiente
        self._env = EnvValores().env_api()

        # Atualiza header
        self.header = self.cria_header_http(
            access_token=self._env['OAUTH_ACCESS_TOKEN'])
        log.info('Fim')

    def solicita_na_api(self, param: str, tentativas_maximo=5, base_delay=1,
                        max_delay=32):
        """
        Faz um GET para a API e retorna o response.json().

        Parameters
        ----------
        param : str
            Rota da solicitação.
        tentativas_maximo : int
            Maximo de tentativas de requisição.
        base_delay : int
            delay inicial.
        max_delay : int
            delay maximo do exponential backoff.

        Raises
        ------
        UnauthorizedError
            Ocorre quando o token de acessor inspira.

        Returns
        -------
        JSON
            Arquivo json do response da requisição.

        """
        log.info(f'Inicia para {param}')
        rota_param = self.rota + param

        # exponential backoff
        tentativas = 0
        while tentativas < tentativas_maximo:
            try:
                log.info(f"Faz requisição {tentativas}")
                response = requests.get(url=rota_param, headers=self.header)

                situationStatusCode = response.status_code
                log.info(f"situation Status Code {situationStatusCode}")
                if situationStatusCode == 401:
                    raise UnauthorizedError(response.json()['error'])

                response.raise_for_status()

                return response.json()

            except UnauthorizedError as e:
                log.error('Credenciais expiradas')
                print(f'\nUnauthorizedError: {e}\n')

                # Solicita novas credenciais de acesso
                self._atualiza_token(self._env['OAUTH_REFRESH_TOKEN'])

                # Refaz o pedido de busca com credencial atualizado
                log.info('Refaz o pedido')
                return self.solicita_na_api(param=param)

            except (RequestException, ConnectionError) as e:
                log.error(f"Erro na tentativa {tentativas + 1}: {e}")
                log.error(f"{type(e)}")

                # Calcula o próximo tempo de espera usando backoff exponencial
                delay = min(base_delay * (2 ** tentativas) +
                            random.uniform(0, 0.1), max_delay)

                log.error(f"Aguardando {delay}s antes de tentar novamente...")
                time.sleep(delay)

                tentativas += 1

        raise Exception("N máximo de tentativas excedido. Falha na operação.")


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-=-=-


if __name__ == "__main__":
    pass
