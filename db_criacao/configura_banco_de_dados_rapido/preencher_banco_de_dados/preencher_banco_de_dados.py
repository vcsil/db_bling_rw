#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
preencher_banco_de_dados.

Script para pegar os dados do Bling e passar para o banco de dados
"""
from bling_api_v3_oauth.BlingV3 import oauth_blingV3, oauth_refresh_blingV3
from Errors import UnauthorizedError

from dotenv import dotenv_values, get_key
from typing import List, Tuple, Dict, Union, Optional
from pathlib import Path
import requests
import os

from tqdm import tqdm
from psycopg import sql
import psycopg
import time

# =-=-=-=-=-=-=-=-=-=-=-=- Carregando chaves de acesso =-=-=-=-=-=-=-=-=-=-=-=-
# Path consegue lidar com diretório em vários Sistemas Operacionais
env_path = Path(".") / ".." / ".." / ".." / ".env"

# Verifica e pega se o access token estiver no .env
OAUTH_ACCESS_TOKEN = get_key(
    dotenv_path=env_path,
    key_to_get="OAUTH_ACCESS_TOKEN")

if not (OAUTH_ACCESS_TOKEN):
    # Solicita novas credenciais de acesso e salva no arquivo .env
    oauth_blingV3(save_env=True, save_txt=False)


def pega_variaveis_ambiente(
        dotenv_path: Union[str, os.PathLike, None]
) -> Dict[str, Optional[str]]:
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
    global env
    env = dotenv_values(dotenv_path=env_path)
    return env


env = pega_variaveis_ambiente(dotenv_path=env_path)

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-=-=-

# =-=-=-=-=-=-=-=-=-=-=-=-= Configurando acesso a API =-=-=-=-=-=-=-=-=-=-=-=-=

# URL API BLing V3
BASE_URL = env['BLING_BASEURL']


def cria_header_http(access_token: str) -> Dict[str, Optional[str]]:
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
    global header
    header = {
      'Accept': 'application/json',
      'Authorization': f"Bearer {access_token}"
    }
    return header


def atualiza_token(refresh_token: str) -> Dict[str, Optional[str]]:
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
    # Faz requisição de novas credenciais
    oauth_refresh_blingV3(
        refresh_token=refresh_token,
        save_env=True,
        save_txt=False
    )
    # Atualiza a variável env com as novas variáveis de ambiente
    env_atualizado = pega_variaveis_ambiente(dotenv_path=env_path)
    # Atualiza header
    header_atualizado = cria_header_http(
        access_token=env_atualizado['OAUTH_ACCESS_TOKEN']
    )
    return header_atualizado


def solicita_na_api(ROTA: str, header: Dict[str, Optional[str]]):
    """
    Faz um GET para a API e retorna o response.json().

    Parameters
    ----------
    ROTA : str
        Rota da solicitação.
    header : Dict[str, Optional[str]]
        Header de aturoização.

    Raises
    ------
    UnauthorizedError
        Ocorre quando o token de acessor inspira.

    Returns
    -------
    JSON
        Arquivo json do response da requisição.

    """
    try:
        response = requests.get(url=ROTA, headers=header)

        situationStatusCode = response.status_code

        if situationStatusCode == 401:
            raise UnauthorizedError(response.json()['error'])

        return response.json()

    except UnauthorizedError as e:
        print(f'UnauthorizedError: {e}')

        # Solicita novas credenciais de acesso
        header_novo = atualiza_token(refresh_token=env['OAUTH_REFRESH_TOKEN'])

        # Refaz o pedido de busca com credencial atualizado
        return solicita_na_api(ROTA=ROTA, header=header_novo)


header = cria_header_http(access_token=env['OAUTH_ACCESS_TOKEN'])

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-=-=-
# Construindo a string de conexão
conn_string = f"""
    dbname={env["POSTGRES_DATABASE"]}
    user={env["POSTGRES_USERNAME"]}
    password={env["POSTGRES_PASSWORD"]}
    host={env["POSTGRES_HOST"]}
    port={env["POSTGRES_PORT"]}
"""

t0 = time.perf_counter()

try:
    # Conecte-se a um banco de dados existente
    with psycopg.connect(conn_string) as conn:

        # Execute a command: this creates a new table
        conn.execute("""
            CREATE TABLE test (
                id serial PRIMARY KEY,
                num integer,
                data text)
            """)

        # Passe os dados para preencher os espaços reservados de uma consulta
        # e deixe o Psycopg executar a conversão correta (sem injeções de SQL!)
        conn.execute(
            "INSERT INTO test (num, data) VALUES (%s, %s)",
            (100, "abc'def"))

        # Consulte o banco de dados e obtenha dados como objetos Python.
        conn.execute("SELECT * FROM test").fetchone()
        # retornará (1, 100, "abc'def")

        # Você pode usar `cur.fetchmany()`, `cur.fetchall()` para retornar uma
        # lista de vários registros, ou até mesmo iterar no cursor
        for record in conn.execute("SELECT * FROM test"):
            print(record)

        # Faça as alterações no banco de dados persistentes
        # conn.commit()


except psycopg.Error as e:
    print(f"Erro ao conectar ao banco de dados: {e}")

finally:
    dt = time.perf_counter() - t0
    print(f'{dt:0.3f}s')
