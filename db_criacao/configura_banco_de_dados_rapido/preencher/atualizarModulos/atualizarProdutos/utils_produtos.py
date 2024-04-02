#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 17:30:41 2024.

@author: vcsil
"""
from preencherModulos.utils import db_inserir_uma_linha
from preencherModulos.preencherProdutos.utils_produtos import (
    _solicita_estoque_fornecedor, produto_insere_saldo_estoque)

from atualizarModulos.utils import (
    db_atualizar_uma_linha, db_verifica_se_existe,
    item_com_valores_atualizados)

import logging

log = logging.getLogger('root')


def atualizar_estoque_fornecedor(tabelas_colunas, id_produto, api, db, conn):
    """Pega saldos da API e atualiza no banco de dados."""
    log.info(f"Atualiza estoque do produto {id_produto}")

    colunas_prod_est = tabelas_colunas["produtos_estoques"][:]
    colunas_prod_est.remove("id")
    colunas_prod_for = tabelas_colunas["produto_fornecedor"][:]

    # Inserir saldo de estoque
    produto_fornecedor, produtos_estoques = _solicita_estoque_fornecedor(
        id_produto=id_produto, api=api)

    db_atualizar_uma_linha(
        tabela="produtos_estoques", colunas=colunas_prod_est,
        valores=produtos_estoques[0],
        coluna_filtro=["id_produto", "id_deposito"],
        valor_filtro=[id_produto, produtos_estoques[0]["id_deposito"]],
        db=db, conn=conn)

    db_atualizar_uma_linha(
        tabela="produto_fornecedor", colunas=colunas_prod_for,
        valores=produto_fornecedor[0], coluna_filtro=["id_bling"],
        valor_filtro=[produto_fornecedor[0]["id_bling"]],
        db=db, conn=conn)


def atualiza_variacao(tabelas_colunas, produto_variacao, variacao,
                      api, db, conn):
    """Atualiza uma variação que já existe."""
    log.info(f"Atualiza variacao do produto {variacao['id_bling']}")

    colunas = tabelas_colunas["produtos"][:]
    colunas_prod_var = tabelas_colunas["produto_variacao"][:]
    colunas_prod_var.remove("id")

    # Atualiza na tabela de produtos
    db_atualizar_uma_linha(
        tabela="produtos", colunas=colunas, db=db,
        valores=variacao, coluna_filtro="id_bling",
        valor_filtro=variacao["id_bling"], conn=conn)

    # Atualiza na tabela produto_variacao
    db_atualizar_uma_linha(
        tabela="produto_variacao",
        colunas=colunas_prod_var, db=db,
        valores=produto_variacao,
        coluna_filtro="id_produto_filho",
        valor_filtro=variacao["id_bling"], conn=conn)

    # Atualiza estoque
    atualizar_estoque_fornecedor(
        tabelas_colunas=tabelas_colunas, db=db,
        id_produto=variacao["id_bling"], api=api,
        conn=conn)


def cria_variacao(tabelas_colunas, produto_variacao, variacao, api, db, conn):
    """Insere uma nova variação."""
    log.info(f"Cria nova variacao, Produto {variacao['id_bling']}")

    colunas = tabelas_colunas["produtos"][:]
    colunas_prod_var = tabelas_colunas["produto_variacao"][:]
    colunas_prod_var.remove("id")

    # Insere produto
    db_inserir_uma_linha(
        tabela="produtos", colunas=colunas, conn=conn,
        valores=variacao, db=db)

    # Insere produto_variacao  # Outra tabela
    db_inserir_uma_linha(
        tabela="produto_variacao", db=db, conn=conn,
        colunas=colunas_prod_var, valores=produto_variacao)

    produto_insere_saldo_estoque(
        tabelas_colunas=tabelas_colunas, api=api,
        id_produto=variacao["id_bling"], db=db, conn=conn)


def solicita_produto_para_atualizar(tabelas_colunas, idProduto, fuso,
                                    api, db, conn):
    """Solicita produto e retorna dict se tiver alteração ou False."""
    variacoes, produto = solicita_produto(
        idProduto=idProduto, api=api, db=db, conn=conn, fuso=fuso,
        tabelas_colunas=tabelas_colunas, inserir_produto=False)

    produto.pop("criado_em")
    produto_modificado = item_com_valores_atualizados(
        item_api=produto, tabela="produtos", coluna_busca="id_bling", api=api,
        db=db, conn=conn, fuso=fuso)

    return variacoes, produto_modificado


def solicita_variacao_para_atualizar(produto_variacao, fuso, variacao, api, db,
                                     conn):
    """Solicita produto e retorna dict pronto para inserir."""
    variacao.pop("criado_em")
    variacao_modificado = item_com_valores_atualizados(
        item_api=variacao, tabela="produtos", coluna_busca="id_bling", api=api,
        db=db, conn=conn, fuso=fuso)

    produto_variacao_modificado = item_com_valores_atualizados(
        item_api=produto_variacao, tabela="produto_variacao", conn=conn,
        coluna_busca="id_produto_filho", api=api, db=db, fuso=fuso)

    return produto_variacao_modificado, variacao_modificado


if __name__ == "__main__":
    pass
