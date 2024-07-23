#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 20:03:55 2024.

@author: vcsil
"""
from config.env_valores import EnvValores
from config.conexao_api import ConectaAPI
from config.conexao_db import ConectaDB

from tqdm import tqdm
import logging
import time
import pytz

log = logging.getLogger("root")

for sec in tqdm(range(99), desc="Esperando configurações do postgres",
                position=1):
    time.sleep(1)

FUSO = pytz.timezone("America/Sao_Paulo")

log.info("Configura conexão com API")
_env_api = EnvValores().env_api()
API = ConectaAPI(_env_api)  # Carrega as variáveis de ambiente necessárias

log.info("Configura conexão com banco de dados")
_env_db = EnvValores().env_db()
DB = ConectaDB(_env_db)  # Carrega as variáveis de ambiente necessárias

log.info("Obtém nome de todas tabelas")
TABELAS_COLUNAS = DB.cria_dict_tabelas_colunas()

log.info("Define diretório para salvar fotos.")
IMAGE_DIR = "../../../local_images/"

if __name__ == "__main__":
    pass
