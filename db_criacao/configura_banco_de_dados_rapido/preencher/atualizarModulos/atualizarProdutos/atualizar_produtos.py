#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 13:06:07 2023.

@author: vcsil
"""
from preencherModulos.preencherProdutos.utils_produtos import (
    solicita_categeoria, solicita_deposito, produto_insere_saldo_estoque,
    solicita_insere_variacao, solicita_produto, insere_segunda_tentativa,
    _solicita_variacao)
from preencherModulos.utils import (
    db_inserir_varias_linhas, db_inserir_uma_linha, api_pega_todos_id)

from atualizarModulos.atualizarProdutos.utils_produtos import (
    atualizar_estoque_fornecedor, atualiza_variacao, cria_variacao)
from atualizarModulos.utils import (
    db_atualizar_uma_linha, db_verifica_se_existe, solicita_novos_ids)

from datetime import date, datetime
from tqdm import tqdm
import logging

log = logging.getLogger('root')

# =-=-=-=-=-=-=-=-=-=-=-=-= Preencher Tabela Produtos =-=-=-=-=-=-=-=-=-=-=-=-=


class AtualizarProdutos():
    """Preenche módulo de produtos."""

    def __init__(self, tabelas_colunas, db):
        self.tabelas_colunas = tabelas_colunas
        self.db = db

    def _atualiza_produtos_tipos(self, tabela: str, sigla, conn):
        """Atualiza a tabela produtos_tipos da database."""
        log.info("Insere novos tipos de contatos")
        colunas = self.tabelas_colunas[tabela][:]
        colunas.remove("id")

        valor = {"nome": sigla, "sigla": sigla}

        return db_inserir_uma_linha(
                tabela=tabela, colunas=colunas, valores=valor,
                db=self.db, conn=conn)

    def _atualiza_produtos_formatos(self, tabela: str, sigla, conn):
        """Atualiza a tabela produtos_formatos da database."""
        log.info("Insere novo formato de produtos")
        colunas = self.tabelas_colunas[tabela][:]
        colunas.remove('id')

        valor = {"nome": sigla, "sigla": sigla}

        return db_inserir_uma_linha(
                tabela=tabela, colunas=colunas, valores=valor,
                db=self.db, conn=conn)

    def _atualiza_produtos_tipo_producao(self, tabela: str, sigla, conn):
        """Atualiza a tabela produtos_tipo_producao da database."""
        log.info("Insere novos tipos de produção de produtos")
        colunas = self.tabelas_colunas[tabela][:]
        colunas.remove('id')

        valor = {"nome": sigla, "sigla": sigla},

        return db_inserir_uma_linha(
            tabela=tabela, colunas=colunas, valores=valor,
            db=self.db, conn=conn)

    def _atualiza_produtos_condicao(self, tabela: str, id_condicao, conn):
        """Atualiza a tabela produtos_condicao da database."""
        log.info("Insere nova condicao de produtos")
        colunas = self.tabelas_colunas[tabela][:]

        valor = {"id": id_condicao, "nome": str(id_condicao)},

        db_inserir_uma_linha(
            tabela=tabela, colunas=colunas, valores=valor,
            db=self.db, conn=conn)
        log.info("Fim de preencher produtos condição")

    def _atualiza_produtos_categorias(self, tabela: str, conn, api):
        """Atualiza a tabela produtos_categorias da database."""
        log.info("Insere novas categorias de produtos.")
        colunas = self.tabelas_colunas[tabela][:]

        ids_categorias = solicita_novos_ids(
            param="/categorias/produtos?", tabela_busca=tabela,
            coluna_busca="id_bling", coluna_retorno="id_bling",
            conn=conn, api=api, db=self.db)

        ROTA = '/categorias/produtos/'
        log.info(f"Passará por {len(ids_categorias)} categorias")
        list_relacao_categoria = []
        for idCategoria in tqdm(ids_categorias, desc="Atualiza categorias"):
            log.info(f"Solicita dados da categoria {idCategoria} na API")
            rel, categoria = solicita_categeoria(rota=ROTA+f"{idCategoria}",
                                                 api=api)

            log.info(f"Insere categoria {idCategoria}")
            db_inserir_uma_linha(
                tabela=tabela, colunas=colunas, valores=categoria,
                db=self.db, conn=conn)

            # Pegando informações sobre relação da categoria
            if rel:
                list_relacao_categoria.append(rel)

        log.info("Insere relacoes das categorias")
        colunas_relacao = (self
                           .tabelas_colunas["produtos_categorias_relacao"][:])
        colunas_relacao.remove("id")
        db_inserir_varias_linhas(tabela="produtos_categorias_relacao",
                                 colunas=colunas_relacao, conn=conn,
                                 db=self.db, valores=list_relacao_categoria)

        log.info("Fim de preencher categorias dos produtos")

    def _atualiza_produtos_depositos(self, tabela: str, conn, api):
        """Atualiza a tabela produtos_depositos da database."""
        colunas = self.tabelas_colunas[tabela][:]

        ids_depositos = solicita_novos_ids(
            param="/depositos?", tabela_busca=tabela, coluna_busca="id_bling",
            coluna_retorno="id_bling", conn=conn, api=api, db=self.db)

        ROTA = '/depositos/'
        log.info(f"Passará por {len(ids_depositos)} depositos")
        for idDeposito in tqdm(ids_depositos, desc="Busca depositos"):
            log.info(f"Solicita dados do deposito {idDeposito} na API")
            deposito = solicita_deposito(rota=ROTA+f"{idDeposito}", api=api)

            log.info("Insere deposito")
            db_inserir_uma_linha(
                tabela=tabela, colunas=colunas, valores=deposito,
                db=self.db,  conn=conn)

        log.info("Fim de atualizar produtos depositos")

    def atualiza_lista_produtos(self, tabela: str, conn, api, fuso):
        """Pega produtos da API e compara com a tabela produtos da database."""
        # Pega todos os produtos Pai e Simples
        ids_produtos = solicita_novos_ids(
            param="/produtos?criterio=5&tipo=T&", tabela_busca=tabela,
            coluna_busca="id_bling", coluna_retorno="id_bling", conn=conn,
            api=api, db=self.db)
        produtos_nao_incluidos = []

        log.info(f"Passará por {len(ids_produtos)} produtos")
        for idProduto in tqdm(ids_produtos, desc="Busca produtos"):
            log.info(f"Solicita dados do produto {idProduto} na API")
            variacoes, produto = solicita_produto(
                idProduto=idProduto, api=api, db=self.db, conn=conn,
                tabelas_colunas=self.tabelas_colunas, fuso=fuso,
                inserir_produto=True)

            # Se o produto não for Pai, será resolvido depois.
            if not produto:
                produtos_nao_incluidos.append(variacoes)
                log.info(f"Produto {idProduto} não incluido de primeira.")
                continue

            # Lida com as variações do produto Pai
            if variacoes:
                for variacao in variacoes:
                    solicita_insere_variacao(
                        dict_variacao=variacao, fuso=fuso, id_Pai=idProduto,
                        tabelas_colunas=self.tabelas_colunas, db=self.db,
                        conn=conn)

                    produto_insere_saldo_estoque(
                        tabelas_colunas=self.tabelas_colunas, api=api,
                        id_produto=variacao["id"], db=self.db, conn=conn)
            else:
                produto_insere_saldo_estoque(
                    tabelas_colunas=self.tabelas_colunas, id_produto=idProduto,
                    api=api, db=self.db, conn=conn)
            conn.commit()

        log.info(f"Passará por {len(produtos_nao_incluidos)} produtos, novame")
        for prod_variacao in tqdm(produtos_nao_incluidos, desc="Repete busca"):
            insere_segunda_tentativa(tabelas_colunas=self.tabelas_colunas,
                                     produto=prod_variacao, fuso=fuso, api=api,
                                     db=self.db, conn=conn)

    def atualiza_valores_produtos(self, tabela, conn, api, fuso):
        """Busca por produtos que foram alterado na data definida."""
        colunas = self.tabelas_colunas[tabela][:]

        # Pega os produtos alterados no dia de hoje
        hoje = date.today()  # - timedelta(days=1)
        param = "/produtos?criterio=1&tipo=P&"
        param += f"dataAlteracaoInicial={hoje}&dataAlteracaoFinal={hoje}&"
        ids_produtos_alterado = api_pega_todos_id(api=api, param=param)

        for idProduto in tqdm(ids_produtos_alterado, desc="Atualiza produtos"):
            # Verifica se ele já eiste no banco de dados
            produto_existe = db_verifica_se_existe(
                tabela_busca="produtos", coluna_busca="id_bling", db=self.db,
                valor_busca=idProduto, colunas_retorno="id_bling", conn=conn)

            log.info(f"Solicita dados do produto {idProduto} na API")
            if produto_existe:
                variacoes, produto = solicita_produto(
                    idProduto=idProduto, api=api, db=self.db, conn=conn,
                    tabelas_colunas=self.tabelas_colunas, fuso=fuso,
                    inserir_produto=False)
                # Atualiza valores do produto
                produto["alterado_em"] = datetime.now(fuso)
                db_atualizar_uma_linha(
                    tabela=tabela, colunas=colunas, valores=produto, conn=conn,
                    coluna_filtro=["id_bling"], valor_filtro=[idProduto],
                    db=self.db)

            else:
                variacoes, produto = solicita_produto(
                    idProduto=idProduto, api=api, db=self.db, conn=conn,
                    tabelas_colunas=self.tabelas_colunas, fuso=fuso,
                    inserir_produto=True)

            # Lida com as variações do produto Pai
            if variacoes:
                for variacao in variacoes:
                    produto_variacao, variacao = _solicita_variacao(
                        variacao=variacao, db=self.db, fuso=fuso,
                        conn=conn, id_pai=idProduto)
                    variacao["alterado_em"] = datetime.now(fuso)

                    # Verifica se a variação já existe no banco de dados
                    variacao_existe = db_verifica_se_existe(
                        tabela_busca="produtos", coluna_busca="id_bling",
                        valor_busca=[variacao["id_bling"]], db=self.db,
                        conn=conn, colunas_retorno="id_bling")
                    if variacao_existe:
                        atualiza_variacao(
                            tabelas_colunas=self.tabelas_colunas, db=self.db,
                            produto_variacao=produto_variacao, conn=conn,
                            variacao=variacao, api=api)

                    else:
                        cria_variacao(
                            tabelas_colunas=self.tabelas_colunas, db=self.db,
                            produto_variacao=produto_variacao, conn=conn,
                            variacao=variacao, api=api)
            else:
                if produto_existe:
                    atualizar_estoque_fornecedor(
                        tabelas_colunas=self.tabelas_colunas, api=api,
                        id_produto=idProduto, db=self.db, conn=conn)
                else:
                    produto_insere_saldo_estoque(
                        tabelas_colunas=self.tabelas_colunas, api=api,
                        id_produto=idProduto, db=self.db, conn=conn)

    def atualizar_modulo_produtos(self, conn, api, fuso):
        """Preencher módulo de produtos."""
        log.info("Inicio")

        log.info("Inicio atualizar categroias de produtos")
        self._atualiza_produtos_categorias(tabela="produtos_categorias",
                                           conn=conn, api=api)

        log.info("Inicio atualizar depositos de produtos")
        self._atualiza_produtos_depositos(tabela="produtos_depositos",
                                          conn=conn, api=api)
        conn.commit()

        log.info("Inicio atualizar lista de produtos")
        self.atualiza_lista_produtos(tabela='produtos', conn=conn, api=api,
                                     fuso=fuso)

        log.info("Inicio atualizar valores de produtos")
        self.atualiza_valores_produtos(tabela='produtos', conn=conn, api=api,
                                       fuso=fuso)

        log.info("Fim produtos")


if __name__ == "__main__":
    pass
