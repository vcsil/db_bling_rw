#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 22:58:45 2024.

@author: vcsil.
"""
from preencherModulos.utils import (db_inserir_uma_linha, db_pega_um_elemento,
                                    api_pega_todos_id,
                                    db_pega_varios_elementos)
from preencherModulos.preencherContas.utils_contas import (
    _manipula_relacao_contas_borderos, _manipula_pagamentos)

from atualizarModulos.utils import (item_com_valores_atualizados,
                                    db_atualizar_uma_linha,
                                    db_verifica_se_existe)
from config.constants import TABELAS_COLUNAS, API

from datetime import date
import logging

log = logging.getLogger("root")


def atualiza_contas(conta, conn):
    """Atualiza ou insere contas novas no banco de dados."""
    log.info("Atualiza conta")

    tabela = "contas_receitas_despesas"
    colunas = TABELAS_COLUNAS[tabela][:]

    conta_existe = db_verifica_se_existe(tabela, "id_bling",
                                         conta["id_bling"], conn)

    parametros = ["vencimento", "data_emissao", "vencimento_original",
                  "competencia"]
    for p in parametros:
        ano, mes, dia = conta[p].split("-")
        conta[p] = date(int(ano), int(mes), int(dia))

    if conta_existe:
        conta_modificada = item_com_valores_atualizados(conta, tabela,
                                                        "id_bling", conn)
        if conta_modificada:
            db_atualizar_uma_linha(tabela, colunas, conta_modificada,
                                   "id_bling", conta["id_bling"], conn)
        return

    log.info("Insere conta")
    db_inserir_uma_linha(tabela, colunas, conta, conn)
    return


def atualiza_bordero(id_conta, id_borderos, conn):
    """Atualiza e insere novos borderos."""
    tabela = "borderos"
    colunas = TABELAS_COLUNAS[tabela][:]

    PARAM = "/borderos/"
    for id_bordero in id_borderos:
        bordero_existe = db_pega_um_elemento(tabela, "id_bling", [id_bordero],
                                             "id_bling", conn)
        if bordero_existe:
            _atualiza_relacao_conta_bordero
            return bordero_existe["id_bling"]

        bordero = API.solicita_na_api(PARAM+str(id_bordero))["data"]

        bordero_db = {
            "id_bling": bordero["id"],
            "data": bordero["data"],
            "historico": bordero["historico"],
            "id_portador": bordero["portador"]["id"],
            "id_categoria_receita_despesa": bordero["categoria"]["id"],
        }
        db_inserir_uma_linha(tabela, colunas, bordero_db, conn)

        _manipula_pagamentos(bordero["pagamentos"], bordero["id"], conn)
        _atualiza_relacao_conta_bordero(id_conta, id_bordero, conn)

    return


def _atualiza_relacao_conta_bordero(id_conta, id_bordero, conn):
    tabela = "contas_borderos_relacao"
    colunas = TABELAS_COLUNAS[tabela][:]
    colunas.remove("id")

    relacao_existe = db_verifica_se_existe(tabela, colunas,
                                           [id_conta, id_bordero], conn)
    if not relacao_existe:
        _manipula_relacao_contas_borderos(id_conta, id_bordero, conn)

    return


def solicita_novos_ids_completo(PARAM, tabela_busca, coluna, conn):
    """Passa por todas as páginas da API."""
    ids_api = api_pega_todos_id(PARAM)

    ids_db = db_pega_varios_elementos(tabela_busca, coluna, conn)
    ids_db = [item[coluna] for item in ids_db]

    ids = list(set(ids_api) - set(ids_db))
    ids.sort()

    return ids
