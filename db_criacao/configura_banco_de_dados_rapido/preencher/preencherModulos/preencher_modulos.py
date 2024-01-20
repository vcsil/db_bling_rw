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
from preencherModulos.preencherContas.preencher_contas import (
    PreencherContas)
from preencherModulos.preencherPedidosVendas.preencher_vendas import (
    PreencherVendas)
from config.env_valores import EnvValores
from config.conexao_api import ConectaAPI
from config.conexao_db import ConectaDB

import logging
import pytz

log = logging.getLogger(__name__)


def preencher_modulos():
    """Preenche todos os módulos."""
    fuso = pytz.timezone("America/Sao_Paulo")

    log.info("Configura conexão com API")
    env_api = EnvValores().env_api()
    api = ConectaAPI(env_api)  # Carrega as variáveis de ambiente necessárias

    log.info("Configura conexão com banco de dados")
    env_db = EnvValores().env_db()
    db = ConectaDB(env_db)  # Carrega as variáveis de ambiente necessárias

    log.info("Obtém nome de todas tabelas")
    tabelas_colunas = db.cria_dict_tabelas_colunas()

    # Inicia conexão com Banco de Dados
    log.info('Inicia preenchimento')
    with db.conectar_ao_banco() as conn:

        log.info("Começa preencher contatos.")
        PreencherContatos(tabelas_colunas, db).preencher_modulo_contatos(conn,
                                                                         api,
                                                                         fuso)
        log.info("Comita contatos")
        conn.commit()
        log.info("Começa preencher produtos.")
        PreencherProdutos(tabelas_colunas, db).preencher_modulo_produtos(conn,
                                                                         api,
                                                                         fuso)
        log.info("Comita produtos")
        conn.commit()

        log.info("Começa preencher contas a receber.")
        PreencherContas(tabelas_colunas, db).preencher_modulo_contas(conn, api,
                                                                     fuso)
        log.info("Comita contas a receber")
        conn.commit()

        log.info("Começa preencher pedidos de venda.")
        PreencherVendas(tabelas_colunas, db).preencher_modulo_vendas(conn, api,
                                                                     fuso)
        log.info("Comita vendas")
        conn.commit()
        print('Foi')


if __name__ == "__main__":
    pass
