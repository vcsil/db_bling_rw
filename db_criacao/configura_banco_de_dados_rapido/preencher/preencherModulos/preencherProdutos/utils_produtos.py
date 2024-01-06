#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 17:29:39 2023.

@author: vcsil
"""
from preencherModulos.utils import (formata_data, db_pega_um_elemento,
                                    verifica_preenche_valor)

from datetime import datetime
import logging

log = logging.getLogger(__name__)

"""Funções utéis para preencher produtos."""


def solicita_categeoria(rota: str, api):
    """Solicita a categoria e retorna os dados e a relação pai/filho."""
    categoria = api.solicita_na_api(rota)['data']
    valores_categoria = _modifica_valores_categoria(categoria)

    log.info("Manipula dados da categoria")
    categoria_pai = categoria["categoriaPai"]["id"]

    if categoria_pai:
        relacao = {"categoria_pai": categoria_pai,
                   "categoria_filho": categoria["id"]}
        return (relacao, valores_categoria)
    else:
        return (False, valores_categoria)


def _modifica_valores_categoria(categoria: dict):
    valores_categoria = {
        "id_bling": categoria["id"],
        "nome": categoria["descricao"]
    }
    return valores_categoria


def solicita_deposito(rota: str, api):
    """Solicita o deposito na API."""
    deposito = api.solicita_na_api(rota)['data']
    log.info("Manipula dados do deposito")
    valores_deposito = _modifica_valores_deposito(deposito)

    return valores_deposito


def _modifica_valores_deposito(deposito: dict):
    valores_deposito = {
        "id_bling": deposito["id"],
        "descricao": deposito["descricao"],
        "situacao": bool(deposito['situacao']),
        "padrao": deposito['padrao'],
        "desconsiderar_saldo": deposito['desconsiderarSaldo'],
    }
    return valores_deposito


def solicita_produto(rota: str, api, conn, fuso):
    """Solicita o produto na API."""
    produto = api.solicita_na_api(rota)['data']
    log.info("Manipula dados do produto")

    if ("variacao" in produto.keys()):
        return (False, False)

    valores_produto = _modifica_valores_produto(produto=produto, conn=conn,
                                                fuso=fuso)

    if len(produto["variacoes"]) > 0:
        variacoes = produto["variacoes"]
        return (variacoes, valores_produto)
    else:
        return (False, valores_produto)


def _modifica_valores_produto(produto: dict, conn, fuso, id_pai=None):
    valores_produto = {
        "id_bling": produto["id"],
        "nome": produto["nome"],
        "codigo": produto["codigo"],
        "preco": int(produto["preco"]*100),
        "id_tipo_produto": db_pega_um_elemento(
            tabela_busca="produtos_tipos", coluna_busca='sigla',
            valor_busca=produto["tipo"], colunas_retorno=["id"],
            conn=conn)["id"],
        "situacao_produto": _formata_situacao_produto(produto["situacao"]),
        "id_formato_produto": db_pega_um_elemento(
            tabela_busca="produtos_formatos", coluna_busca='sigla',
            valor_busca=produto["formato"], colunas_retorno=["id"],
            conn=conn)["id"],
        "id_produto_pai": id_pai,
        "descricao_curta": produto["descricaoCurta"],
        "data_validade": formata_data(produto["dataValidade"]),
        "unidade": produto["unidade"],
        "peso_liquido": int(produto["pesoLiquido"]*100),
        "peso_bruto": int(produto["pesoBruto"]*100),
        "volumes": produto["volumes"],
        "itens_por_caixa": produto["itensPorCaixa"],
        "gtin": produto["gtin"],
        "gtin_embalagem": produto["gtinEmbalagem"],
        "id_tipo_producao": db_pega_um_elemento(
            tabela_busca="produtos_tipo_producao", coluna_busca='sigla',
            valor_busca=produto["tipoProducao"], colunas_retorno=["id"],
            conn=conn)["id"],
        "id_condicao_producao": produto["condicao"],
        "frete_gratis": produto["freteGratis"],
        "marca": produto["marca"],
        "descricao_complementar": produto["descricaoComplementar"],
        "link_externo": produto["linkExterno"],
        "observacoes": produto["observacoes"],
        "id_categoria_produto": produto["categoria"]["id"],
        "estoque_minimo": produto["estoque"]["minimo"],
        "estoque_maximo": produto["estoque"]["maximo"],
        "estoque_crossdocking": produto["estoque"]["crossdocking"],
        "estoque_localizacao": produto["estoque"]["localizacao"],
        "id_dimensoes": _formata_dimensoes(dimensoes_api=produto["dimensoes"],
                                           conn=conn),
        "ncm": produto["tributacao"]["ncm"],
        "cest": produto["tributacao"]["cest"],
        "id_midia_principal": _formata_midia(
            url_midia=produto["midia"]["imagens"]["externas"], conn=conn),
        "criado_em": datetime.now(fuso)
    }
    for chave, valor in valores_produto.items():
        if (valor == ''):
            valores_produto[chave] = None

    return valores_produto


def _formata_situacao_produto(situacao):
    """'Ativo': True, 'Inativo': False."""
    if (situacao == "A"):
        return True
    elif (situacao == "I"):
        return False


def _formata_dimensoes(dimensoes_api, conn):
    for key in dimensoes_api.keys():
        if key != "unidadeMedida":
            dimensoes_api[key] = int(dimensoes_api[key] * 100)
    colunas = list(dimensoes_api.keys())
    colunas[colunas.index("unidadeMedida")] = "unidade_medida"
    valores = list(dimensoes_api.values())

    id_dimensao = verifica_preenche_valor(
        tabela_busca="dimensoes", coluna_busca=colunas, valor_busca=valores,
        list_colunas=['id']+colunas, conn=conn)

    return id_dimensao


def _formata_midia(url_midia, conn):
    coluna = "url"

    if len(url_midia) > 0:
        valor = url_midia[0]

        id_midia = verifica_preenche_valor(
            tabela_busca="produtos_midias", coluna_busca=coluna,
            valor_busca=valor, list_colunas=["id", "tipo", "url"], conn=conn)
        return id_midia
    else:
        return None


def solicita_variacao(variacao: dict, id_pai: int, fuso, conn):
    """Monta objeto variacao."""
    valores_produto = _modifica_valores_produto(
        produto=variacao, conn=conn, fuso=fuso, id_pai=id_pai)

    produto_variacao = _modifica_produto_variacao(variacao, id_pai)
    return (produto_variacao, valores_produto)


def _modifica_produto_variacao(produto, id_pai):
    produto_variacao = {
        "id_produto_pai": id_pai,
        "id_produto_filho": produto['id'],
        "nome": produto["variacao"]["nome"],
        "ordem": produto["variacao"]["ordem"],
        "clone_pai": produto["variacao"]["produtoPai"]["cloneInfo"]
    }
    return produto_variacao


def solicita_estoque_fornecedor(id_produto: int, api):
    """Solicita saldo e estoque na api."""
    rota1 = "/estoques/saldos?idsProdutos[]=" + str(id_produto)
    produto_estoque = api.solicita_na_api(rota1)['data'][0]

    log.info("Manipula dados dos produtos_estoques")
    saldo_produto = _modifica_produto_estoque(saldos=produto_estoque)

    rota2 = "/produtos/fornecedores?idProduto=" + str(id_produto)
    produto_fornecedor = api.solicita_na_api(rota2)['data']

    log.info("Manipula dados dos produto_fornecedor")
    fornecedor_produto = _modifica_produto_fornecedor(
        fornecedor=produto_fornecedor)

    return (fornecedor_produto, saldo_produto)


def _modifica_produto_estoque(saldos: dict):
    list_produto_estoque = []
    for idx in range(len(saldos["depositos"])):
        produto_estoque = {
            "id_produto": saldos["produto"]["id"],
            "id_deposito": saldos["depositos"][idx]["id"],
            "saldo_fisico": saldos["depositos"][idx]["saldoFisico"],
            "saldo_virtual": saldos["depositos"][idx]["saldoVirtual"]
        }
        list_produto_estoque.append(produto_estoque)
    return list_produto_estoque


def _modifica_produto_fornecedor(fornecedor: dict):
    list_produto_fornecedor = []
    for idx in range(len(fornecedor)):
        id_fornecedor = fornecedor[idx]["fornecedor"]["id"]
        id_fornecedor = id_fornecedor if id_fornecedor != 0 else None
        produto_fornecedor = {
            "id_bling": fornecedor[idx]["id"],
            "descricao": fornecedor[idx]["descricao"],
            "codigo": fornecedor[idx]["codigo"],
            "preco_custo": int(fornecedor[idx]["precoCusto"]*100),
            "preco_compra": int(fornecedor[idx]["precoCompra"]*100),
            "padrao": fornecedor[idx]["padrao"],
            "id_produto": fornecedor[idx]["produto"]["id"],
            "id_fornecedor": id_fornecedor
        }
        list_produto_fornecedor.append(produto_fornecedor)
    return list_produto_fornecedor


if __name__ == "__main__":
    pass
