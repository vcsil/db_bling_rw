#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 13:06:07 2023.

@author: vcsil
"""
from preencherModulos.preencherProdutos.utils_produtos import (
    solicita_categeoria, solicita_deposito, produto_insere_saldo_estoque,
    solicita_insere_variacao, solicita_produto, solicita_ids_produtos,
    insere_segunda_tentativa)
from preencherModulos.utils import (
    db_inserir_varias_linhas, api_pega_todos_id, db_inserir_uma_linha)
from config.constants import TABELAS_COLUNAS

from tqdm import tqdm
import logging

log = logging.getLogger("root")

# =-=-=-=-=-=-=-=-=-=-=-=-= Preencher Tabela Produtos =-=-=-=-=-=-=-=-=-=-=-=-=


class PreencherProdutos():
    """Preenche módulo de produtos."""

    def __init__(self):
        pass

    def preencher_produtos_tipos(self, conn):
        """Preenche a tabela produtos_tipos da database."""
        tabela = "produtos_tipos"
        colunas = TABELAS_COLUNAS[tabela][:]
        colunas.remove("id")

        valores = [
            {"nome": "Serviço", "sigla": "S"},
            {"nome": "Produto", "sigla": "P"},
            {"nome": "Serviço 06 21 22", "sigla": "N"},
        ]

        log.info("Insere tipos de contatos")
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Fim de preencher produtos tipos")

    def preencher_produtos_formatos(self, conn):
        """Preenche a tabela produtos_formatos da database."""
        tabela = "produtos_formatos"
        colunas = TABELAS_COLUNAS[tabela][:]
        colunas.remove("id")

        valores = [
            {"nome": "Simples", "sigla": "S"},
            {"nome": "Com variações", "sigla": "V"},
            {"nome": "Com composição", "sigla": "E"},
        ]

        log.info("Insere formatos de produtos")
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Fim de preencher produtos formatos")

    def preencher_produtos_tipo_producao(self, conn):
        """Preenche a tabela produtos_formatos da database."""
        tabela = "produtos_tipo_producao"
        colunas = TABELAS_COLUNAS[tabela][:]
        colunas.remove("id")

        valores = [
            {"nome": "Própria", "sigla": "P"},
            {"nome": "Terceiros", "sigla": "T"},
        ]

        log.info("Insere tipos de produção de produtos")
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Fim de preencher produtos tipo producão")

    def preencher_produtos_condicao(self, conn):
        """Preenche a tabela produtos_condicao da database."""
        tabela = "produtos_condicao"
        colunas = TABELAS_COLUNAS[tabela][:]

        valores = [
            {"id": "0", "nome": "Não especificado"},
            {"id": "1", "nome": "Novo"},
            {"id": "2", "nome": "Usado"},
        ]

        log.info("Insere condicao de produtos")
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Fim de preencher produtos condição")

    def preencher_produtos_categorias(self, conn):
        """Preenche a tabela produtos_formatos da database."""
        tabela = "produtos_categorias"
        colunas = TABELAS_COLUNAS[tabela][:]
        ids_categorias = api_pega_todos_id("/categorias/produtos?")
        ids_categorias += [6071256]  # Categoria Padrão
        ids_categorias.sort()

        ROTA = "/categorias/produtos/"
        log.info(f"Passará por {len(ids_categorias)} categorias")
        list_relacao_categoria = []
        for idCategoria in tqdm(ids_categorias, desc="Busca categorias",
                                position=1):
            log.info(f"Solicita dados da categoria {idCategoria} na API")
            rel, categoria = solicita_categeoria(rota=ROTA+f"{idCategoria}")

            log.info("Insere categoria")
            db_inserir_uma_linha(tabela, colunas, categoria, conn)

            # Pegando informações sobre relação da categoria
            if rel:
                list_relacao_categoria.append(rel)

        log.info("Insere relacoes das categorias")
        colunas_relacao = TABELAS_COLUNAS["produtos_categorias_relacao"][:]
        colunas_relacao.remove("id")
        db_inserir_varias_linhas("produtos_categorias_relacao",
                                 colunas_relacao, list_relacao_categoria, conn)

        log.info("Fim de preencher categorias dos produtos")

    def preencher_produtos_depositos(self, conn):
        """Preenche a tabela produtos_depositos da database."""
        tabela = "produtos_depositos"
        colunas = TABELAS_COLUNAS[tabela][:]
        ids_depositos = api_pega_todos_id("/depositos?")
        ids_depositos.sort()

        ROTA = "/depositos/"
        log.info(f"Passará por {len(ids_depositos)} depositos")
        for idDeposito in tqdm(ids_depositos, desc="Busca depositos",
                               position=1):
            log.info(f"Solicita dados do deposito {idDeposito} na API")
            deposito = solicita_deposito(rota=ROTA+f"{idDeposito}")

            log.info("Insere deposito")
            db_inserir_uma_linha(tabela, colunas, deposito, conn)

        log.info("Fim de preencher produtos depositos")

    def preencher_produtos(self, conn):
        """Preenche a tabela produtos da database."""
        # Pega todos os produtos Pai e Simples
        ids_produtos = solicita_ids_produtos()
        produtos_nao_incluidos = []

        log.info(f"Passará por {len(ids_produtos)} produtos")
        for idProduto in tqdm(ids_produtos, desc="Busca produtos", position=1):
            log.info(f"Solicita dados do produto {idProduto} na API")
            variacoes, produto = solicita_produto(idProduto, conn,
                                                  inserir_produto=True)

            # Se o produto não for Pai, será resolvido depois.
            if not produto:
                produtos_nao_incluidos.append(variacoes)
                log.info(f"Produto {idProduto} não incluido de primeira.")
                continue

            # Lida com as variações do produto Pai
            if variacoes:
                for variacao in variacoes:
                    solicita_insere_variacao(variacao, idProduto, conn)

                    produto_insere_saldo_estoque(variacao["id"], conn)
            else:
                produto_insere_saldo_estoque(idProduto, conn)

        log.info(f"Passará por {len(produtos_nao_incluidos)} produtos, novame")
        for prod_variacao in tqdm(produtos_nao_incluidos, desc="Repete busca",
                                  position=1):
            insere_segunda_tentativa(prod_variacao, conn)

    def preencher_modulo_produtos(self, conn):
        """Preencher módulo de produtos."""
        log.info("Inicio")

        log.info("Inicio preencher produtos_tipos")
        self.preencher_produtos_tipos(conn)

        log.info("Inicio preencher produtos_formatos")
        self.preencher_produtos_formatos(conn)

        log.info("Inicio preencher produtos_tipo_producao")
        self.preencher_produtos_tipo_producao(conn)

        log.info("Inicio preencher produtos_condicao")
        self.preencher_produtos_condicao(conn)

        log.info("Inicio preencher produtos_categorias")
        self.preencher_produtos_categorias(conn)

        log.info("Inicio preencher produtos_depositos")
        self.preencher_produtos_depositos(conn)

        log.info("Inicio preencher produtos")
        self.preencher_produtos(conn)

        log.info("Fim produtos")


if __name__ == "__main__":
    pass
