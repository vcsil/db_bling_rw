#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 19:21:19 2024.

@author: vcsil
"""
from preencherModulos.utils import (
    possui_informacao, db_inserir_uma_linha, db_inserir_varias_linhas,
    manipula_dados_endereco, verifica_preenche_valor, _verifica_contato,
    db_pega_varios_elementos_controi_filtro)
from config.constants import API, TABELAS_COLUNAS

import logging

log = logging.getLogger("root")

# =-=-=-=-=-=-=-=-=- Funções utéis para preencher produtos. =-=-=-=-=-=-=-=-=-=


def solicita_preenche_venda(rota: str, conn):
    """Solicita a conta e retorna os dados da conta manipulados."""
    venda = API.solicita_na_api(rota)["data"]
    log.info("Manipula dados de venda")
    _verifica_contato(venda["contato"]["id"], conn)
    _modifica_insere_valores_vendas(venda, conn)

    _modifica_insere_volumes(venda, conn)
    _modifica_insere_itens_produtos(venda["itens"], venda["id"], conn)
    _modifica_insere_parcelas(venda, conn)


def _modifica_insere_valores_vendas(venda: dict, conn):
    dataPrevista = venda["dataPrevista"]
    numeroLoja = venda["numeroLoja"]
    numeroPedidoCompra = venda["numeroPedidoCompra"]
    observacoes = venda["observacoes"]
    observacoesInternas = venda["observacoesInternas"]
    id_categoria = venda["categoria"]["id"]
    id_vendedor = venda["vendedor"]["id"]

    transporte = venda["transporte"]
    t_contato = transporte["contato"]["id"]
    valores_venda = {
        "id_bling": venda["id"],
        "numero": venda["numero"],
        "numero_loja": numeroLoja if numeroLoja else None,
        "data": venda["data"],
        "data_saida": venda["dataSaida"],
        "data_prevista": dataPrevista if int(dataPrevista[0]) else None,
        "id_contato": venda["contato"]["id"],
        "id_situacao": venda["situacao"]["id"],
        "situacao_valor": venda["situacao"]["valor"],
        "id_loja": venda["loja"]["id"],
        "numero_pedido_compra": (numeroPedidoCompra if numeroPedidoCompra
                                 else None),
        "outras_despesas": round(venda["outrasDespesas"]*100),
        "observacoes": observacoes if observacoes else None,
        "observacoes_internas": (observacoesInternas if observacoesInternas
                                 else None),
        "desconto": round(venda["desconto"]["valor"]*100),
        "desconto_unidade": venda["desconto"]["unidade"],
        "id_categoria": id_categoria if id_categoria else None,
        "id_nota_fiscal": venda["notaFiscal"]["id"],
        "total_icms": venda["tributacao"]["totalICMS"],
        "total_ipi": venda["tributacao"]["totalIPI"],
        "id_vendedor": id_vendedor if id_vendedor else None,
        "transporte_id_frete_por_conta": transporte["fretePorConta"],
        "transporte_valor_frete": round(transporte["frete"]*100),
        "transporte_quantidade_volumes": transporte["quantidadeVolumes"],
        "transporte_peso_bruto": round(transporte["pesoBruto"]*100),
        "transporte_prazo_entrega": transporte["prazoEntrega"],
        "transporte_id_contato": t_contato if bool(t_contato) else None,
        "transporte_id_etiqueta": _modifica_insere_etiqueta(
            transporte["etiqueta"], conn),
        "alterado_em": None,
    }
    log.info("Insere pedido de venda")

    db_inserir_uma_linha("vendas", list(valores_venda.keys()), valores_venda,
                         conn)


def _modifica_insere_etiqueta(etiqueta: dict, conn):
    log.info("Insere etiqueta de transporte da venda")
    etiqueta["nomePais"] = "Brasil"
    if possui_informacao(etiqueta):
        list_colunas = TABELAS_COLUNAS["endereco_paises"]
        id_pais = verifica_preenche_valor("endereco_paises", "nome",
                                          etiqueta["nomePais"], list_colunas,
                                          conn)
        endereco = manipula_dados_endereco(etiqueta, id_pais, conn)

        # Inserir na tabela enderecos
        valores = list(endereco.values())
        colunas = list(endereco.keys())
        id_endereco = verifica_preenche_valor("enderecos", colunas, valores,
                                              ["id"]+colunas, conn)

        nome = etiqueta["nome"]
        valores_etiqueta = {
            "nome": nome if nome else None,
            "id_endereco": id_endereco
        }

        return db_inserir_uma_linha("transporte_etiqueta",
                                    list(valores_etiqueta.keys()),
                                    valores_etiqueta, conn)["id"]

    else:
        return None


def _modifica_insere_volumes(venda: dict, conn):
    log.info("Insere volumes da venda")
    volumes = venda["transporte"]["volumes"]
    if len(volumes) > 0:
        id_venda = venda["id"]
        list_volumes = []
        for volume in volumes:
            valores_etiqueta = {
                "id_bling": volume["id"],
                "id_venda": id_venda,
                "servico": volume["servico"],
                "codigo_rastreamento": volume["codigoRastreamento"]
            }
            list_volumes.append(valores_etiqueta)

        db_inserir_varias_linhas("transporte_volumes",
                                 list(valores_etiqueta.keys()), list_volumes,
                                 conn)


def _modifica_insere_itens_produtos(venda_itens: list, id_venda: int, conn):
    log.info("Insere produtos da venda")
    list_venda_itens = []

    if len(venda_itens) > 0:
        for item in venda_itens:
            id_produto = item["produto"]["id"]
            obj_item = {
                "id_bling": item["id"],
                "id_venda": id_venda,
                "id_produto": id_produto if id_produto else None,
                "desconto": round(item["desconto"]*100),
                "valor": round(item["valor"]*100),
                "quantidade": item["quantidade"]
            }
            list_venda_itens.append(obj_item)

        db_inserir_varias_linhas("vendas_itens_produtos",
                                 list(obj_item.keys()), list_venda_itens, conn)


def _modifica_insere_parcelas(venda: dict, conn):
    log.info("Insere parcelas da venda")
    venda_parcelas = venda["parcelas"]

    if len(venda_parcelas) > 0:
        contas = _busca_conta_receber(venda, conn)

        id_venda = venda["id"]
        list_venda_parcelas = []
        for parcela in venda_parcelas:
            valor = round(parcela["valor"]*100)
            id_conta_receber = None
            if len(contas) > 0:
                for conta in contas:
                    if conta["valor"] == valor:
                        id_conta_receber = conta["id_bling"]
                        contas.remove(conta)
                        break
                # Quando a venda é feita pelo cartão há o desconto das taxas
                # O valor recebido vai ser diferente
                if not id_conta_receber:
                    id_conta_receber = contas[0]["id_bling"]
                    contas.pop(0)

            observacoes = parcela["observacoes"]
            obj_parcela = {
                "id_bling": parcela["id"],
                "id_venda": id_venda,
                "data_vencimento": parcela["dataVencimento"],
                "valor": valor,
                "observacoes": observacoes if observacoes else None,
                "id_forma_pagamento": parcela["formaPagamento"]["id"],
                "id_conta_receber": id_conta_receber
            }
            list_venda_parcelas.append(obj_parcela)

        db_inserir_varias_linhas("parcelas", list(obj_parcela.keys()),
                                 list_venda_parcelas, conn)


def _busca_conta_receber(venda: dict, conn):
    filtro = f"WHERE vencimento_original='{venda['data']}' "
    filtro += f"AND id_vendedor={venda['vendedor']['id']} "
    filtro += f"AND id_contato={venda['contato']['id']} AND historico LIKE "
    filtro += f"'%Ref. ao pedido de venda nº {venda['numero']}%'"

    colunas_retorno = ["id_bling", "valor", "id_portador"]

    return db_pega_varios_elementos_controi_filtro("contas_receitas_despesas",
                                                   filtro, colunas_retorno,
                                                   conn)


if __name__ == "__main__":
    pass
