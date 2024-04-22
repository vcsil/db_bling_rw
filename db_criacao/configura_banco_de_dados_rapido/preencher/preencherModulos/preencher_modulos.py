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
from config.constants import DB

import logging

log = logging.getLogger('root')


def preencher_modulos():
    """Preenche todos os módulos."""
    # Inicia conexão com Banco de Dados
    log.info('Inicia preenchimento')
    with DB.conectar_ao_banco() as conn:

        log.info("Começa preencher contatos.")
        PreencherContatos().preencher_modulo_contatos(conn)
        log.info("Comita contatos")
        conn.commit()

        log.info("Começa preencher produtos.")
        PreencherProdutos().preencher_modulo_produtos(conn)
        log.info("Comita produtos")
        conn.commit()

        log.info("Começa preencher contas a receber.")
        PreencherContas().preencher_modulo_contas(conn)
        log.info("Comita contas a receber")
        conn.commit()

        log.info("Começa preencher pedidos de venda.")
        PreencherVendas().preencher_modulo_vendas(conn)
        log.info("Comita vendas")
        conn.commit()
        print('Foi')


if __name__ == "__main__":
    pass
