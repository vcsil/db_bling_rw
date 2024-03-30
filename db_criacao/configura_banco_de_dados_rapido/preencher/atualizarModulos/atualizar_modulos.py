#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 14:21:42 2024.

@author: vcsil
"""
from atualizarModulos.atualizarContatos.atualiza_contatos import (
    AtualizarContatos)
from atualizarModulos.atualizarProdutos.atualizar_produtos import (
    AtualizarProdutos)
from atualizarModulos.atualizarContas.atualizar_contas import (
    AtualizarContas)
from atualizarModulos.atualizarPedidosVendas.atualizar_vendas import (
    AtualizarVendas)

from config.env_valores import EnvValores
from config.conexao_api import ConectaAPI
from config.conexao_db import ConectaDB

import logging
import pytz

log = logging.getLogger(__name__)


def atualizar_modulos():
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
    log.info('Inicia atualização')
    with db.conectar_ao_banco() as conn:

        log.info("Começa atualizar contatos.")
        AtualizarContatos(tabelas_colunas, db).atualizar_modulo_contatos(conn,
                                                                         api,
                                                                         fuso)
        log.info("Comita contatos")
        conn.commit()

        log.info("Começa a atualizar produtos.")
        AtualizarProdutos(tabelas_colunas, db).atualizar_modulo_produtos(conn,
                                                                         api,
                                                                         fuso)
        log.info("Comita produtos")
        conn.commit()

        log.info("Começa atualizar contas a receber.")
        AtualizarContas(tabelas_colunas, db).atualizar_modulo_contas(conn, api,
                                                                     fuso)
        log.info("Comita contas a receber")
        conn.commit()

        log.info("Começa atualizar pedidos de venda.")
        AtualizarVendas(tabelas_colunas, db).atualizar_modulo_vendas(conn, api,
                                                                     fuso)
        log.info("Comita vendas")
        conn.commit()
        print('Foi')


if __name__ == "__main__":
    pass