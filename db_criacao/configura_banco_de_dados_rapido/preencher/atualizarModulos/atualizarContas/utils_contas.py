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
    _manipula_relacao_contas_borderos, _manipula_pagamentos,
    manipula_origem_conta_receber)

from atualizarModulos.utils import (item_com_valores_atualizados,
                                    db_atualizar_uma_linha,
                                    db_verifica_se_existe)
from config.constants import TABELAS_COLUNAS, API

from datetime import date, timedelta
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
            _atualiza_relacao_conta_bordero(id_conta, id_bordero, conn)
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


def solicita_contas_receber(DATA_AGORA):
    """Solicita ids das contas a recebe para serem atualizadas."""
    PARAM = "/contas/receber?"
    PARAM += "&".join(list(map(lambda n: "situacoes[]="+str(n), range(1, 6))))

    # Atualizará as contas dos últimos 20 dias na última hora do dia.
    intervalo_dias = 20 if DATA_AGORA.hour >= 23 else 0
    data_busca = str((DATA_AGORA - timedelta(days=intervalo_dias)).date())
    PARAM_BUSCA = f"&dataInicial={data_busca}&"
    PARAM_BUSCA += f"dataFinal={str(DATA_AGORA.date())}&"

    # Busca pela data de emissão
    PARAM_BUSCA1 = PARAM_BUSCA + "tipoFiltroData=E&"
    contas_receber1 = api_pega_todos_id(PARAM + PARAM_BUSCA1)
    # Busca pela data de vencimento
    PARAM_BUSCA2 = PARAM_BUSCA + "tipoFiltroData=V&"
    contas_receber2 = api_pega_todos_id(PARAM + PARAM_BUSCA2)

    contas_receber = list(set(contas_receber1 + contas_receber2))
    return contas_receber


def solicita_contas_pagar(DATA_AGORA):
    """Solicita ids das contas a pagar para serem atualizadas."""
    PARAM = "/contas/pagar?"

    intervalo_dias = 10 if DATA_AGORA.hour >= 23 else 0
    data_busca = str((DATA_AGORA - timedelta(days=intervalo_dias)).date())

    # Busca pela data de emissão
    PARAM1 = f"dataEmissaoInicial={data_busca}&"
    PARAM1 += f"dataEmissaoFinal={str(DATA_AGORA.date())}&"
    contas_pagar = api_pega_todos_id(PARAM+PARAM1)

    # Busca pela data de pagamento
    PARAM2 = f"dataPagamentoInicial={data_busca}&"
    PARAM2 += f"dataPagamentoFinal={str(DATA_AGORA.date())}&"
    contas_pagar += api_pega_todos_id(PARAM+PARAM2)

    # Busca pela data de vencimento
    PARAM3 = f"dataVencimentoInicial={data_busca}&"
    PARAM3 += f"dataVencimentoFinal={str(DATA_AGORA.date())}&"
    contas_pagar += api_pega_todos_id(PARAM+PARAM3)

    contas_pagar = list(set(contas_pagar))
    return contas_pagar


def atualiza_origem_conta(id_conta, origem: dict, conn):
    """Verifica atualizações na origem da conta."""
    if not origem:
        return

    tabela = "contas_origens"
    colunas = TABELAS_COLUNAS[tabela][:]

    origem_existe = db_verifica_se_existe(tabela, ["id_bling", "id_conta"],
                                          [origem["id"], id_conta], conn)

    if origem_existe:
        origem_api = manipula_origem_conta_receber(origem, id_conta, conn,
                                                   False)

        origem_modificada = item_com_valores_atualizados(origem_api, tabela,
                                                         "id_bling", conn)
        if origem_modificada:
            db_atualizar_uma_linha(tabela, colunas, origem_modificada,
                                   "id_bling", origem_api["id_bling"], conn)
    else:
        origem = manipula_origem_conta_receber(origem, id_conta, conn, True)

    return
