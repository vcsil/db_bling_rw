#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 00:48:45 2024.

@author: vcsil
"""
from config.constants import API, TABELAS_COLUNAS
from preencherModulos.utils import (_verifica_contato, db_inserir_uma_linha,
                                    db_inserir_varias_linhas, formata_data,
                                    db_pega_um_elemento)

from datetime import timedelta
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

    origem_conta_receber = conta.pop("origem", None)

    return valores_forma_pagamento, conta["borderos"], origem_conta_receber


def _modifica_valores_conta(conta: dict, conn):
    id_portador = conta["portador"]["id"]
    formaPagamento = conta["formaPagamento"]["id"]
    numero_documento = conta["numeroDocumento"]
    id_transacao = conta.pop("idTransacao", None)
    link_qr_code_pix = conta.pop("linkQRCodePix", None)
    link_boleto = conta.pop("linkBoleto", None)
    id_vendedor = _manipula_valor_opcional(conta, "vendedor", "id")

    valores_conta = {
        "id_bling": conta["id"],
        "id_situacao": conta["situacao"],
        "vencimento": conta["vencimento"],
        "valor": round(conta["valor"]*100),
        "id_transacao": id_transacao if id_transacao else None,
        "link_qr_code_pix": link_qr_code_pix if link_qr_code_pix else None,
        "link_boleto": link_boleto if link_boleto else None,
        "data_emissao": conta["dataEmissao"],
        "id_contato": conta["contato"]["id"],
        "id_forma_pagamento": formaPagamento if formaPagamento else None,
        "saldo": round(conta["saldo"]*100),
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
        "alterado_em": None,
    }
    return valores_conta


def manipula_bordero(id_borderos: list, id_conta, conn):
    """Preenche a tabela de boderos."""
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

        if secundario == "diaVencimento":
            if valor:
                valor = _soma_data(conta["dataEmissao"], valor).date()

        if secundario == "dataLimite":
            ano = valor.split("-")[0]
            if ano == "0000":
                valor = None

        return valor

    return None


def _soma_data(data, dias):
    data = formata_data(data)
    return data + timedelta(days=dias)


def manipula_origem_conta_receber(origem: dict, id_conta, conn, insere=True):
    """Manipula e insere linha relacionado a origem da conta a receber."""
    tabela = "contas_origens"
    colunas = TABELAS_COLUNAS[tabela][:]
    colunas.remove("id")

    valores_origem = {
        "id_origem": origem["id"],
        "id_conta": id_conta,
        "tipo_origem": origem["tipoOrigem"],
        "numero": origem["numero"],
        "data_emissao": formata_data(origem["dataEmissao"]),
        "valor": round(origem["valor"]*100),
        "id_conta_origem_situacao": origem["situacao"],
        "url": origem["url"]
    }

    if insere:
        db_inserir_uma_linha(tabela, colunas, valores_origem, conn)

    return valores_origem


if __name__ == "__main__":
    pass
