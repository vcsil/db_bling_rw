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

# =-=-=-=-=-=-=-=-=-=-=-=-= Conexão ao Banco de Dados =-=-=-=-=-=-=-=-=-=-=-=-=

# Construindo a string de conexão
conn_string = f"""
    dbname={env["POSTGRES_DATABASE"]}
    user={env["POSTGRES_USERNAME"]}
    password={env["POSTGRES_PASSWORD"]}
    host={env["POSTGRES_HOST"]}
    port={env["POSTGRES_PORT"]}
"""


def select_all_from_db(
        tabela: str,
        colunas: Union[str, List[str]],
        conn_string: str,
        filtro: Tuple[str, Tuple[Union[str, int]]] = None
) -> List[Tuple[int]]:
    """
    Faz um SELECT no banco de dados.

    É possivel definir a tabela, as colunas e algum tipo de filtro

    Parameters
    ----------
    tabela : str
        Nome da tabela.
    colunas : Union[str, List[str]]
        Nome da coluna ou um array com o nome das colunas .
    conn_string : str
        String de conexão com banco de dados.
    filtro : Tuple[str, Tuple[Union[str, int]]], optional
        Uma tupla com o Filtro seguindo por uma tupla com o valor do filtro.
        The default is None.

    Returns
    -------
    List[Tuple[int]]
        Uma lista com as linhas em forma de tupla com os dados.

    """
    if isinstance(colunas, str):
        colunas = [colunas]

    query = (
        sql.SQL("SELECT {columns} FROM {table}")
        .format(
            columns=sql.SQL(',').join(
                    map(sql.Identifier, colunas)
            ),
            table=sql.SQL(tabela)
        )
    )
    if filtro:
        query = sql.SQL("{query_fixa} {fltr} {tabela}").format(
            query_fixa=query,
            fltr=sql.SQL(filtro[0]),
            tabela=sql.Literal(filtro[1])
        )

    try:
    # Conecte-se a um banco de dados existente
        with psycopg.connect(conn_string) as conn:
            # print(query.as_string(conn))
            array_dados = conn.execute(query).fetchall()

        return array_dados
    except psycopg.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
                id serial PRIMARY KEY,
                num integer,
                data text)
            """)

        # Passe os dados para preencher os espaços reservados de uma consulta
        # e deixe o Psycopg executar a conversão correta (sem injeções de SQL!)
        conn.execute(
            "INSERT INTO test (num, data) VALUES (%s, %s)",
            (100, "abc'def"))

def insert_in_db(
        tabela: str,
        colunas: Union[str, List[str]],
        valores: List[Dict[str, Union[str, int]]],
        valores_placeholder: List[str],
        conn_string: str
):
    """
    Faz um INSERT no banco de dados.

    Parameters
    ----------
    tabela : str
        Nome da tabela.
    colunas : Union[str, List[str]]
        Nome da coluna.
    valores : List[Dict[str, Union[str, int]]]
        Uma lista com os valores a serem inseridos em tupla.
        Nome da coluna.
    valores_placeholder : List[str]
        Lista utilizada para nomear cada coluna que vai receber o valor.

    Returns
    -------
    None.

    """
    query = (
        sql.SQL("INSERT INTO {table} ({columns}) VALUES ({values})")
        .format(
            table=sql.Identifier(tabela),
            columns=sql.SQL(',').join(
                    map(sql.Identifier, colunas)
            ),
            values=sql.SQL(', ').join(
                    map(sql.Placeholder, valores_placeholder)
            )
        )
    )

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.executemany(query, valores)
    except psycopg.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")


def pega_nome_colunas(tabela: str) -> List[str]:
    """
    Pegar o nome de todas as colunas de uma tabela.

    Parameters
    ----------
    tabela : str
        Nome da tabela.

    Returns
    -------
    array_dados : List[str]
        Lista de tupla com os nomes das colunas.

    """
    nome_colunas = select_all_from_db(tabela='"information_schema"."columns"',
                                      colunas="column_name",
                                      filtro=("WHERE table_name =", tabela),
                                      conn_string=conn_string)
    # Tirar os valores da tupla e deixar dentro de uma array
    nome_colunas = [coluna[0] for coluna in nome_colunas]

    return nome_colunas

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
