#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 00:48:45 2024.

@author: vcsil
"""
from preencherModulos.utils import _verifica_contato
import logging

log = logging.getLogger('root')

"""Funções utéis para preencher produtos."""


def solicita_formas_pagamento(rota: str, api):
    """Solicita e retorna os dados das formas de pagamento."""
    forma_pag = api.solicita_na_api(rota)['data']
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


def solicita_categeoria(rota: str, api):
    """Solicita a categoria e retorna os dados e a relação pai/filho."""
    categoria = api.solicita_na_api(rota)['data']
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


def solicita_vendedor(rota: str, api):
    """Solicita vendedor e retorna os dados manipulados."""
    vendedor = api.solicita_na_api(rota)['data']
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


def solicita_conta(rota: str, api, tabelas_colunas, conn, db, fuso):
    """Solicita a conta e retorna os dados da conta manipulados."""
    conta = api.solicita_na_api(rota)['data']
    _verifica_contato(id_contato=conta["contato"]["id"], api=api, conn=conn,
                      tabelas_colunas=tabelas_colunas, db=db, fuso=fuso)
    log.info("Manipula dados da forma de pagamento")
    valores_forma_pagamento = _modifica_valores_conta(conta)

    return valores_forma_pagamento


def _modifica_valores_conta(conta: dict):
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
        "id_bordero": _manipula_bordero(conta["borderos"]),
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


def _manipula_bordero(bordero: list):
    id_bordero = None
    for id_b in bordero:
        id_bordero = id_b
    return id_bordero


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
