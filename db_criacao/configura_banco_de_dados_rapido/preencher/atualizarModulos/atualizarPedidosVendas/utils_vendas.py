#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 15:34:54 2024.

@author: vcsil
"""

from preencherModulos.utils import (
    possui_informacao, db_inserir_uma_linha,  manipula_dados_endereco,
    verifica_preenche_valor, _verifica_contato, db_pega_um_elemento,
    db_pega_varios_elementos_controi_filtro)

from atualizarModulos.utils import (db_verifica_se_existe,
                                    db_atualizar_uma_linha,
                                    item_com_valores_atualizados)

from config.constants import API, DB, FUSO, TABELAS_COLUNAS
from datetime import datetime
import logging

log = logging.getLogger('root')

# =-=-=-=-=-=-=-=-=- Funções utéis para preencher vendas. =-=-=-=-=-=-=-=-=-=


def solicita_preenche_venda(rota: str, conn):
    """Solicita a conta e retorna os dados da conta manipulados."""
    venda = API.solicita_na_api(rota)['data']

    id_contato = venda["contato"]["id"]
    _verifica_contato(id_contato, TABELAS_COLUNAS, API, DB, conn, FUSO)
    existe_venda = db_verifica_se_existe("vendas", "id_bling", venda["id"],
                                         conn)

    log.info("Manipula dados de venda")
    _modifica_insere_valores_vendas(venda, existe_venda, conn)

    _modifica_insere_volumes(venda, existe_venda, conn)
    _modifica_insere_itens_produtos(venda["itens"], venda["id"], existe_venda,
                                    conn)
    _modifica_insere_parcelas(venda, existe_venda, conn)


def _modifica_insere_valores_vendas(venda: dict, existe, conn):
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
        "data": datetime.strptime(venda["data"], "%Y-%m-%d"),
        "data_saida": datetime.strptime(venda["dataSaida"], "%Y-%m-%d").date(),
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
            transporte["etiqueta"], existe, venda["id"], conn),
        "alterado_em": None
    }
    log.info("Insere pedido de venda")

    if existe:
        valores_venda.pop("data")
        valores_venda.pop("alterado_em")
        valores_venda_att = item_com_valores_atualizados(valores_venda,
                                                         "vendas", "id_bling",
                                                         conn)

        if valores_venda_att:
            db_atualizar_uma_linha("vendas", list(valores_venda_att.keys()),
                                   valores_venda_att, ["id_bling"],
                                   valores_venda["id_bling"], conn)
    else:
        db_inserir_uma_linha("vendas", list(valores_venda.keys()),
                             valores_venda, DB, conn)


def _modifica_insere_etiqueta(etiqueta: dict, existe, id_venda, conn):
    log.info("Insere etiqueta de transporte da venda")
    etiqueta["nomePais"] = "Brasil"
    if possui_informacao(etiqueta):
        id_pais = verifica_preenche_valor('endereco_paises', 'nome',
                                          etiqueta["nomePais"],
                                          TABELAS_COLUNAS["endereco_paises"],
                                          conn=conn, db=DB)
        endereco = manipula_dados_endereco(etiqueta, id_pais, DB, conn,
                                           TABELAS_COLUNAS)

        # Inserir na tabela enderecos
        valores = list(endereco.values())
        colunas = list(endereco.keys())
        id_endereco = verifica_preenche_valor("enderecos", colunas, valores,
                                              ["id"]+colunas, DB, conn)

        nome = etiqueta["nome"]
        valores_etiqueta = {
            "nome": nome if nome else None,
            "id_endereco": id_endereco
        }

        if existe:
            dict_transporte = db_pega_um_elemento("vendas", "id_bling",
                                                  [id_venda],
                                                  "transporte_id_etiqueta",
                                                  DB, conn)
            return dict_transporte["transporte_id_etiqueta"]
        else:
            return db_inserir_uma_linha("transporte_etiqueta",
                                        list(valores_etiqueta.keys()),
                                        valores_etiqueta, DB, conn)["id"]

    else:
        return None


def _modifica_insere_volumes(venda: dict, existe, conn):
    log.info("Insere volumes da venda")

    tabela = "transporte_volumes"
    volumes = venda["transporte"]["volumes"]
    if len(volumes) > 0:
        id_venda = venda["id"]
        for volume in volumes:
            valores_etiqueta = {
                "id_bling": volume["id"],
                "id_venda": id_venda,
                "servico": volume["servico"],
                "codigo_rastreamento": volume["codigoRastreamento"]
            }

            valor_filtro = valores_etiqueta["id_bling"]
            if existe:
                db_atualizar_uma_linha(tabela,
                                       colunas=list(valores_etiqueta.keys()),
                                       valores=valores_etiqueta,
                                       coluna_filtro=["id_bling"],
                                       valor_filtro=valor_filtro,
                                       conn=conn)
            else:
                db_inserir_uma_linha(tabela,
                                     colunas=list(valores_etiqueta.keys()),
                                     valores=valores_etiqueta, db=DB,
                                     conn=conn)


def _modifica_insere_itens_produtos(venda_itens: list, id_venda: int, existe,
                                    conn):
    log.info("Insere produtos da venda")
    tabela = "vendas_itens_produtos"

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

            if existe:
                db_atualizar_uma_linha(tabela, colunas=list(obj_item.keys()),
                                       valores=obj_item,
                                       coluna_filtro="id_bling",
                                       valor_filtro=obj_item["id_bling"],
                                       conn=conn)
            else:
                db_inserir_uma_linha(tabela, colunas=list(obj_item.keys()),
                                     valores=obj_item, db=DB, conn=conn)


def _modifica_insere_parcelas(venda: dict, existe, conn):
    log.info("Insere parcelas da venda")
    venda_parcelas = venda["parcelas"]

    if len(venda_parcelas) > 0:
        contas = _busca_conta_receber(venda, conn)

        id_venda = venda["id"]
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

            if existe:
                db_atualizar_uma_linha(tabela="parcelas",
                                       colunas=list(obj_parcela.keys()),
                                       valores=obj_parcela,
                                       coluna_filtro=["id_bling"],
                                       valor_filtro=obj_parcela["id_bling"],
                                       conn=conn)
            else:
                db_inserir_uma_linha(tabela="parcelas",
                                     colunas=list(obj_parcela.keys()),
                                     valores=obj_parcela, db=DB, conn=conn)


def _busca_conta_receber(venda: dict, conn):
    filtro = f"WHERE vencimento_original='{venda['data']}' "
    filtro += f"AND id_vendedor={venda['vendedor']['id']} "
    filtro += f"AND id_contato={venda['contato']['id']} AND historico LIKE "
    filtro += f"'%Ref. ao pedido de venda nº {venda['numero']}%'"

    colunas_retorno = ["id_bling", "valor", "id_portador"]

    tabela = "contas_receitas_despesas"
    return db_pega_varios_elementos_controi_filtro(tabela, filtro,
                                                   colunas_retorno, DB, conn)


if __name__ == "__main__":
    pass
