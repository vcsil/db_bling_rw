#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 20:03:55 2024.

@author: vcsil
"""
from config.env_valores import EnvValores
from config.conexao_api import ConectaAPI
from config.conexao_db import ConectaDB

import logging
import pytz

log = logging.getLogger('root')

FUSO = pytz.timezone("America/Sao_Paulo")

log.info("Configura conexão com API")
_env_api = EnvValores().env_api()
API = ConectaAPI(_env_api)  # Carrega as variáveis de ambiente necessárias

log.info("Configura conexão com banco de dados")
_env_db = EnvValores().env_db()
DB = ConectaDB(_env_db)  # Carrega as variáveis de ambiente necessárias

log.info("Obtém nome de todas tabelas")
TABELA_COLUNAS = DB.cria_dict_tabelas_colunas()
