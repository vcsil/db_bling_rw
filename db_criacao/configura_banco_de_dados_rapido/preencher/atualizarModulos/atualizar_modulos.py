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
from preencherModulos.utils import db_inserir_uma_linha
from atualizarModulos.utils import txt_fundo_amarelo

from config.constants import FUSO, DB

from datetime import datetime
import logging

log = logging.getLogger("root")


def atualizar_modulos():
    """Preenche todos os módulos."""
    # Inicia conexão com Banco de Dados
    log.info("Inicia atualização")
    DATA_AGORA = datetime.now(FUSO)

    with DB.conectar_ao_banco() as conn:

        log.info("Começa atualizar contatos.")
        AtualizarContatos().atualizar_modulo_contatos(conn)
        log.info("Comita contatos")
        conn.commit()

        log.info("Começa a atualizar produtos.")
        AtualizarProdutos(DATA_AGORA).atualizar_modulo_produtos(conn)
        log.info("Comita produtos")
        conn.commit()

        log.info("Começa atualizar contas a receber.")
        AtualizarContas(DATA_AGORA).atualizar_modulo_contas(conn)
        log.info("Comita contas a receber")
        conn.commit()

        log.info("Começa atualizar pedidos de venda.")
        AtualizarVendas(DATA_AGORA).atualizar_modulo_vendas(conn)
        log.info("Comita vendas")
        conn.commit()

        agora = datetime.now(FUSO)
        db_inserir_uma_linha(
            tabela="atualizacoes_modulos", colunas=["datetime"],
            valores={"datetime": agora}, conn=conn)
        conn.commit()

    txt_fundo_amarelo(f"Atualizado {agora}")
    log.info(f"Atualizado {agora}")


if __name__ == "__main__":
    pass
