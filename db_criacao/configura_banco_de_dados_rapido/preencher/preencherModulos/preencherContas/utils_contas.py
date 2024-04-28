#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 00:48:45 2024.

@author: vcsil
"""
from config.constants import API, TABELAS_COLUNAS
from preencherModulos.utils import (_verifica_contato, db_inserir_uma_linha,
                                    db_inserir_varias_linhas,
                                    db_pega_um_elemento)

import logging

log = logging.getLogger("root")

"""Funções utéis para preencher produtos."""


def solicita_formas_pagamento(rota: str):
    """Solicita e retorna os dados das formas de pagamento."""
    forma_pag = API.solicita_na_api(rota)["data"]
    log.info("Manipula dados da forma de pagamento")
    valores_forma_pagamento = _modifica_valores_formas_pagamento(forma_pag)

    return valores_forma_pagamento


def _modifica_valores_formas_pagamento(forma_pag: dict):
    valores_forma_pagamento = {
        "id_bling": forma_pag["id"],
        "nome": forma_pag["descricao"],
        "id_tipo_pagamento": forma_pag["tipoPagamento"],
        "situacao": bool(forma_pag["situacao"]),
        "fixa": forma_pag["fixa"],
        "id_padrao": forma_pag["padrao"],
        "condicao": forma_pag["condicao"],
        "id_destino": forma_pag["destino"],
        "id_finalidade": forma_pag["finalidade"],
        "taxas_aliquota": forma_pag["taxas"]["aliquota"],
        "taxas_valor": forma_pag["taxas"]["valor"],
        "taxas_prazo": forma_pag["taxas"]["prazo"],
    }
    return valores_forma_pagamento


def solicita_categeoria(rota: str):
    """Solicita a categoria e retorna os dados e a relação pai/filho."""
    categoria = API.solicita_na_api(rota)["data"]
    valores_categoria = _modifica_valores_categoria(categoria)

    log.info("Manipula dados da categoria")
    categoria_pai = categoria["idCategoriaPai"]

    if categoria_pai:
        relacao = {"id_categoria_pai": categoria_pai,
                   "id_categoria_filho": categoria["id"]}
        return (relacao, valores_categoria)
    else:
        return (False, valores_categoria)


def _modifica_valores_categoria(categoria: dict):
    valores_categoria = {
        "id_bling": categoria["id"],
        "nome": categoria["descricao"],
        "id_tipo": categoria["tipo"],
        "situacao": bool(categoria["situacao"])
    }
    return valores_categoria


def solicita_vendedor(rota: str):
    """Solicita vendedor e retorna os dados manipulados."""
    vendedor = API.solicita_na_api(rota)["data"]
    log.info("Manipula dados da forma de pagamento")
    valores_forma_pagamento = _modifica_valores_vendedor(vendedor)

    return valores_forma_pagamento


def _modifica_valores_vendedor(vendedor: dict):
    valores_vendedor = {
        "id_bling": vendedor["id"],
        "desconto_limite": vendedor["descontoLimite"],
        "id_loja": vendedor["loja"]["id"],
        "comissoes_desconto_maximo": round(
            vendedor["comissoes"][0]["descontoMaximo"]*100),
        "comissoes_aliquota": vendedor["comissoes"][0]["aliquota"],
        "id_contato": vendedor["contato"]["id"],
    }
    return valores_vendedor


def solicita_conta(rota: str, conn):
    """Solicita a conta e retorna os dados da conta manipulados."""
    conta = API.solicita_na_api(rota)["data"]
    _verifica_contato(conta["contato"]["id"], conn)
    log.info("Manipula dados da forma de pagamento")
    valores_forma_pagamento = _modifica_valores_conta(conta, conn)

    return valores_forma_pagamento, conta["borderos"]


def _modifica_valores_conta(conta: dict, conn):
    id_portador = conta["portador"]["id"]
    formaPagamento = conta["formaPagamento"]["id"]
    numero_documento = conta["numeroDocumento"]
    id_vendedor = _manipula_valor_opcional(conta, "vendedor", "id")
    valores_conta = {
        "id_bling": conta["id"],
        "id_situacao": conta["situacao"],
        "vencimento": conta["vencimento"],
        "valor": round(conta["valor"]*100),
        "id_contato": conta["contato"]["id"],
        "id_forma_pagamento": formaPagamento if formaPagamento else None,
        "saldo": round(conta["saldo"]*100),
        "data_emissao": conta["dataEmissao"],
        "vencimento_original": conta["vencimentoOriginal"],
        "numero_documento": numero_documento if numero_documento else None,
        "competencia": conta["competencia"],
        "historico": conta["historico"],
        "numero_banco": conta["numeroBanco"] if conta["numeroBanco"] else None,
        "id_portador": id_portador if id_portador else None,
        "id_categoria_receita_despesa": conta["categoria"]["id"],
        "id_vendedor": id_vendedor if id_vendedor else None,
        "id_tipo_ocorrencia": _manipula_valor_opcional(conta, "ocorrencia",
                                                       "tipo"),
        "considerar_dias_uteis": _manipula_valor_opcional(
            conta, "ocorrencia", "considerarDiasUteis"),
        "dia_vencimento": _manipula_valor_opcional(conta, "ocorrencia",
                                                   "diaVencimento"),
        "numero_parcelas": _manipula_valor_opcional(conta, "ocorrencia",
                                                    "numeroParcelas"),
        "data_limite": _manipula_valor_opcional(conta, "ocorrencia",
                                                "dataLimite"),
    }
    return valores_conta


def _manipula_bordero(id_borderos: list, id_conta, conn):
    tabela = "borderos"
    colunas = TABELAS_COLUNAS[tabela][:]

    PARAM = "/borderos/"
    for id_bordero in id_borderos:
        bordero_existe = db_pega_um_elemento(tabela, "id_bling", [id_bordero],
                                             "id_bling", conn)
        if bordero_existe:
            _manipula_relacao_contas_borderos(id_conta, id_bordero, conn)
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
        _manipula_relacao_contas_borderos(id_conta, id_bordero, conn)

    return


def _manipula_pagamentos(pagamentos: list, id_bordero, conn):
    tabela = "pagamentos"
    colunas = TABELAS_COLUNAS[tabela][:]
    colunas.remove("id")

    list_pagamentos = []
    for pagamento in pagamentos:
        pagamento_db = {
            "id_bordero": id_bordero,
            "id_contato": pagamento["contato"]["id"],
            "numero_documento": pagamento["numeroDocumento"],
            "valor_pago": round(pagamento["valorPago"]*100),
            "juros": round(pagamento["juros"]*100),
            "desconto": round(pagamento["desconto"]*100),
            "acrescimo": round(pagamento["acrescimo"]*100),
            "tarifa": round(pagamento["tarifa"]*100),
        }
        list_pagamentos.append(pagamento_db)

    db_inserir_varias_linhas(tabela, colunas, list_pagamentos, conn)
    return


def _manipula_relacao_contas_borderos(id_conta, id_bordero, conn):
    tabela = "contas_borderos_relacao"
    colunas = TABELAS_COLUNAS[tabela][:]
    colunas.remove("id")

    contas_borderos_relacao = {
        "id_conta": id_conta,
        "id_bordero": id_bordero,
    }
    db_inserir_uma_linha(tabela, colunas, contas_borderos_relacao, conn)
    return


def _manipula_valor_opcional(conta: dict, principal: str, secundario: str):
    """Verifica se o valor existe dentro do dict ou retorna None."""
    conta_copy = conta.copy()
    dict2 = conta_copy.pop(principal, None)

    if dict2:
        valor = dict2.pop(secundario, None)
        return valor

    return None


if __name__ == "__main__":
    pass
