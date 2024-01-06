#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 17:09:21 2023.

@author: vcsil
"""
from preencherModulos.preencherContatos.preencher_contatos import (
    PreencherContatos)
from preencherModulos.preencherProdutos.preencher_produtos import (
    PreencherProdutos)
from config.conexao_db import ConectaDB
from config.conexao_api import ConectaAPI

import logging
import pytz

log = logging.getLogger(__name__)


def preencher_modulos():
    """Preenche todos os módulos."""
    fuso = pytz.timezone("America/Sao_Paulo")

    log.info("Configura conexão com API")
    api = ConectaAPI()  # Carrega as variáveis de ambiente necessárias

    log.info("Configura conexão com banco de dados")
    db = ConectaDB()  # Carrega as variáveis de ambiente necessárias

    log.info("Obtem nome de todas tabelas")
    tabelas_colunas = db.cria_dict_tabelas_colunas()

    # Inicia conexão com Banco de Dados
    log.info('Inicia preencimento')
    with db.conectar_ao_banco() as conn:

        # PreencherContatos(tabelas_colunas).preencher_modulo_contatos(conn,
        #                                                            api, fuso)

        PreencherProdutos(tabelas_colunas).preencher_modulo_produtos(conn,
                                                                     api, fuso)
        print('Foi')


if __name__ == "__main__":
    pass
