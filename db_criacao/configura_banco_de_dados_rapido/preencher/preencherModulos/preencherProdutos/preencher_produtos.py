#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 13:06:07 2023.

@author: vcsil
"""
from preencherModulos.preencherProdutos.utils_produtos import (
    solicita_categeoria, solicita_deposito, solicita_produto,
    solicita_estoque_fornecedor, solicita_variacao)
from preencherModulos.utils import (
    db_inserir_varias_linhas, pega_todos_id, db_inserir_uma_linha)

from tqdm import tqdm
import logging

log = logging.getLogger(__name__)

# =-=-=-=-=-=-=-=-=-=-=-=-= Preencher Tabela Contatos =-=-=-=-=-=-=-=-=-=-=-=-=


class PreencherProdutos():
    """Preenche módulo de produtos."""

    def __init__(self, tabelas_colunas):
        self.tabelas_colunas = tabelas_colunas

    def preencher_produtos_tipos(self, tabela: str, conn):
        """Preenche a tabela produtos_tipos da database."""
        colunas = self.tabelas_colunas[tabela][:]
        colunas.remove("id")

        valores = [
            {"nome": 'Serviço', "sigla": 'S'},
            {"nome": 'Produto', "sigla": 'P'},
            {"nome": 'Serviço 06 21 22', "sigla": 'N'},
        ]

        log.info("Insere tipos de contatos")
        db_inserir_varias_linhas(
            tabela=tabela, colunas=colunas, valores=valores, conn=conn)
        log.info("Fim")

    def preencher_produtos_formatos(self, tabela: str, conn):
        """Preenche a tabela produtos_formatos da database."""
        colunas = self.tabelas_colunas[tabela][:]
        colunas.remove('id')

        valores = [
            {"nome": 'Simples', "sigla": 'S'},
            {"nome": 'Com variações', "sigla": 'V'},
            {"nome": 'Com composição', "sigla": 'E'},
        ]

        log.info("Insere formatos de produtos")
        db_inserir_varias_linhas(
            tabela=tabela, colunas=colunas, valores=valores, conn=conn)
        log.info("Fim")

    def preencher_produtos_tipo_producao(self, tabela: str, conn):
        """Preenche a tabela produtos_formatos da database."""
        colunas = self.tabelas_colunas[tabela][:]
        colunas.remove('id')

        valores = [
            {"nome": 'Própria', "sigla": 'P'},
            {"nome": 'Terceiros', "sigla": 'T'},
        ]

        log.info("Insere tipos de produção de produtos")
        db_inserir_varias_linhas(
            tabela=tabela, colunas=colunas, valores=valores, conn=conn)
        log.info("Fim")

    def preencher_produtos_condicao(self, tabela: str, conn):
        """Preenche a tabela produtos_formatos da database."""
        colunas = self.tabelas_colunas[tabela][:]

        valores = [
            {"id": '0', "nome": 'Não especificado'},
            {"id": '1', "nome": 'Novo'},
            {"id": '2', "nome": 'Usado'},
        ]

        log.info("Insere condicao de produtos")
        db_inserir_varias_linhas(
            tabela=tabela, colunas=colunas, valores=valores, conn=conn)
        log.info("Fim")

    def preencher_produtos_categorias(self, tabela: str, conn, api):
        """Preenche a tabela produtos_formatos da database."""
        colunas = self.tabelas_colunas[tabela][:]
        ids_categorias = pega_todos_id(api, '/categorias/produtos?')
        ids_categorias += [6071256]

        ROTA = '/categorias/produtos/'
        log.info(f"Passará por {len(ids_categorias)} categorias")
        list_relacao_categoria = []
        for idCategoria in tqdm(ids_categorias, desc="Busca categorias"):
            log.info(f"Solicita dados da categoria {idCategoria} na API")
            rel, categoria = solicita_categeoria(rota=ROTA+f"{idCategoria}",
                                                 api=api)

            # Pegando informações sobre relação da categoria
            if rel:
                list_relacao_categoria.append(rel)

            log.info("Insere categoria")
            db_inserir_uma_linha(
                tabela=tabela, colunas=colunas, valores=categoria, conn=conn)

        log.info("Insere relacoes das categorias")
        colunas_relacao = (self
                           .tabelas_colunas["produtos_categorias_relacao"][:])
        colunas_relacao.remove("id")
        db_inserir_varias_linhas(tabela="produtos_categorias_relacao",
                                 colunas=colunas_relacao, conn=conn,
                                 valores=list_relacao_categoria)

        log.info("Fim")

    def preencher_produtos_depositos(self, tabela: str, conn, api):
        """Preenche a tabela produtos_depositos da database."""
        colunas = self.tabelas_colunas[tabela][:]
        ids_depositos = pega_todos_id(api, '/depositos?')

        ROTA = '/depositos/'
        log.info(f"Passará por {len(ids_depositos)} depositos")
        for idDeposito in tqdm(ids_depositos, desc="Busca depositos"):
            log.info(f"Solicita dados do deposito {idDeposito} na API")
            deposito = solicita_deposito(rota=ROTA+f"{idDeposito}", api=api)

            log.info("Insere deposito")
            db_inserir_uma_linha(
                tabela=tabela, colunas=colunas, valores=deposito, conn=conn)

        log.info("Fim")

    def preencher_produtos(self, tabela: str, conn, api, fuso):
        """Preenche a tabela produtos da database."""
        colunas = self.tabelas_colunas[tabela][:]

        colunas_produto_variacao = self.tabelas_colunas["produto_variacao"][:]
        colunas_produto_variacao.remove('id')

        colunas_produto_estoques = self.tabelas_colunas["produtos_estoques"][:]
        colunas_produto_estoques.remove('id')

        colunas_produto_forncdr = self.tabelas_colunas["produto_fornecedor"][:]

        ids_produtos = pega_todos_id(api, '/produtos?criterio=5&tipo=T&')
        ids_produtos.sort()
        # [15965567236, 16184005002, 16184005009, 16184005011]
        # If formato == f
        ROTA = "/produtos/"
        log.info(f"Passará por {len(ids_produtos)} produtos")
        for idProduto in tqdm(ids_produtos, desc="Busca produtos"):
            log.info(f"Solicita dados do produto {idProduto} na API")
            variacoes, produto = solicita_produto(
               rota=ROTA+f"{idProduto}", api=api, conn=conn, fuso=fuso)

            if not produto:
                log.info(f"Produto {idProduto} pulado pois é uma variação")
                continue

            log.info(f"Insere produto {idProduto} no banco de dados")
            db_inserir_uma_linha(tabela="produtos", colunas=colunas,
                                 valores=produto, conn=conn)
            if variacoes:
                for variacao in variacoes:
                    log.info(f"Insere variacao {variacao}")
                    log.info(f"Remove produto {variacao} da lista")
                    ids_produtos.remove(variacao["id"])
                    produto_variacao, produto = solicita_variacao(
                        variacao=variacao, fuso=fuso, conn=conn,
                        id_pai=idProduto)

                    log.info(f"Insere produto {variacao} no banco de dados")
                    db_inserir_uma_linha(tabela="produtos", colunas=colunas,
                                         valores=produto, conn=conn)

                    log.info("Insere produto_variacao")  # Outra tabela
                    db_inserir_uma_linha(
                        tabela="produto_variacao", valores=produto_variacao,
                        colunas=colunas_produto_variacao, conn=conn)

                    log.info("Insere saldos de estoque e fornecedor")
                    produto_fornecedor, produtos_estoques = (
                        solicita_estoque_fornecedor(id_produto=variacao["id"],
                                                    api=api))
                    db_inserir_varias_linhas(
                        tabela="produtos_estoques", conn=conn,
                        colunas=colunas_produto_estoques,
                        valores=produtos_estoques)
                    db_inserir_varias_linhas(
                        tabela="produto_fornecedor", conn=conn,
                        colunas=colunas_produto_forncdr,
                        valores=produto_fornecedor)
            else:
                log.info("Insere saldos de estoque e fornecedor")
                produto_fornecedor, produtos_estoques = (
                    solicita_estoque_fornecedor(id_produto=idProduto, api=api))
                db_inserir_varias_linhas(
                    tabela="produtos_estoques", conn=conn,
                    colunas=colunas_produto_estoques,
                    valores=produtos_estoques)
                db_inserir_varias_linhas(
                    tabela="produto_fornecedor", conn=conn,
                    colunas=colunas_produto_forncdr,
                    valores=produto_fornecedor)

    def preencher_modulo_produtos(self, conn, api, fuso):
        """Preencher módulo de produtos."""
        log.info("Inicio")

        log.info("Inicio preencher produtos_tipos")
        self.preencher_produtos_tipos(tabela='produtos_tipos', conn=conn)

        log.info("Inicio preencher produtos_formatos")
        self.preencher_produtos_formatos(tabela='produtos_formatos', conn=conn)

        log.info("Inicio preencher produtos_tipo_producao")
        self.preencher_produtos_tipo_producao(tabela='produtos_tipo_producao',
                                              conn=conn)

        log.info("Inicio preencher produtos_condicao")
        self.preencher_produtos_condicao(tabela='produtos_condicao', conn=conn)

        log.info("Inicio preencher produtos_categorias")
        self.preencher_produtos_categorias(tabela='produtos_categorias',
                                           conn=conn, api=api)

        log.info("Inicio preencher produtos_depositos")
        self.preencher_produtos_depositos(tabela='produtos_depositos',
                                          conn=conn, api=api)

        log.info("Inicio preencher produtos")
        self.preencher_produtos(tabela='produtos', conn=conn, api=api,
                                fuso=fuso)

        log.info("Fim produtos")


if __name__ == "__main__":
    pass
