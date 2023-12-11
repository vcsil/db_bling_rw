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

# Path consegue lidar com diretório em vários Sistemas Operacionais
arquivo_env = Path(".") / ".." / ".." / ".." / ".env"

# Pega os valores das variáveis de ambiente
env = dotenv_values(dotenv_path=arquivo_env)

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
