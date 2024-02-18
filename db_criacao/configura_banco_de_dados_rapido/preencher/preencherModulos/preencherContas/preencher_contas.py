#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 19:01:03 2024.

@author: vcsil
"""
from preencherModulos.preencherContas.utils_contas import (
    solicita_formas_pagamento, solicita_categeoria, solicita_conta,
    solicita_vendedor)
from preencherModulos.utils import (
    db_inserir_varias_linhas, api_pega_todos_id, db_inserir_uma_linha)

from tqdm import tqdm
import logging

log = logging.getLogger(__name__)

# =-=-=-=-=-=-=-=-=-=-=-=-=- Preencher Tabela Contas =-=-=-=-=-=-=-=-=-=-=-=-=-


class PreencherContas():
    """Preenche módulo de contas."""

    def __init__(self, tabelas_colunas, db):
        self.tabelas_colunas = tabelas_colunas
        self.db = db

    def preencher_contas_situacao(self, tabela: str, conn):
        """Preenche a tabela produtos_tipos da database."""
        colunas = self.tabelas_colunas[tabela][:]

        valores = [
            {"id": 1, "nome": "Em aberto"},
            {"id": 2, "nome": "Recebido"},
            {"id": 3, "nome": "Parcialmente recebido"},
            {"id": 4, "nome": "Devolvido"},
            {"id": 5, "nome": "Cancelado"},
        ]

        log.info("Insere situação contas receber")
        db_inserir_varias_linhas(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)
        log.info("Fim de preencher situação contas receber")

    def preencher_tipos_pagamento(self, tabela: str, conn):
        """Preenche a tabela produtos_tipos da database."""
        colunas = self.tabelas_colunas[tabela][:]

        valores = [
            {"id": 1, "nome": "Dinheiro"},
            {"id": 2, "nome": "Cheque"},
            {"id": 3, "nome": "Cartão de Crédito"},
            {"id": 4, "nome": "Cartão de Débito"},
            {"id": 5, "nome": "Crédito Loja"},
            {"id": 10, "nome": "Vale Alimentação"},
            {"id": 11, "nome": "Vale Refeição"},
            {"id": 12, "nome": "Vale Presente"},
            {"id": 13, "nome": "Vale Combustível"},
            {"id": 14, "nome": "Duplicata Mercantil"},
            {"id": 15, "nome": "Boleto Bancário"},
            {"id": 16, "nome": "Depósito Bancário"},
            {"id": 17, "nome": "Pagamento Instantâneo (PIX)"},
            {"id": 18, "nome": "Transferência Bancária, Carteira Digital"},
            {"id": 19,
             "nome": "Programa de Fidelidade, Cashback, Crédito Virtual"},
            {"id": 90, "nome": "Sem pagamento"},
            {"id": 99, "nome": "Outros"},
        ]

        log.info("Insere tipos de pagamento")
        db_inserir_varias_linhas(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)
        log.info("Fim de preencher tipos de pagamento")

    def preencher_formas_pagamento_padrao(self, tabela: str, conn):
        """Preenche a tabela formas_pagamento_padrao da database."""
        colunas = self.tabelas_colunas[tabela][:]

        valores = [
            {"id": 0, "nome": "Não"},
            {"id": 1, "nome": "Padrão"},
            {"id": 2, "nome": "Padrão devolução"},
        ]

        log.info("Insere padrões de pagamento")
        db_inserir_varias_linhas(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)
        log.info("Fim de preencher padrões de pagamento")

    def preencher_formas_pagamento_destino(self, tabela: str, conn):
        """Preenche a tabela formas_pagamento_destino da database."""
        colunas = self.tabelas_colunas[tabela][:]

        valores = [
            {"id": 1, "nome": "Conta a receber/pagar"},
            {"id": 2, "nome": "Ficha financeira"},
            {"id": 3, "nome": "Caixa e bancos"},
        ]

        log.info("Insere destino de pagamento")
        db_inserir_varias_linhas(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)
        log.info("Fim de preencher destino de pagamento")

    def preencher_formas_pagamento_finalidade(self, tabela: str, conn):
        """Preenche a tabela formas_pagamento_finalidade da database."""
        colunas = self.tabelas_colunas[tabela][:]

        valores = [
            {"id": 1, "nome": "Pagamentos"},
            {"id": 2, "nome": "Recebimentos"},
            {"id": 3, "nome": "Pagamentos e Recebimentos"},
        ]

        log.info("Insere finalidade de pagamento")
        db_inserir_varias_linhas(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)
        log.info("Fim de preencher finalidade de pagamento")

    def preencher_formas_pagamento(self, tabela: str, conn, api):
        """Preenche a tabela formas_pagamento da database."""
        colunas = self.tabelas_colunas[tabela][:]
        ids_formas_pagamento = api_pega_todos_id(api, '/formas-pagamentos?')
        ids_formas_pagamento.sort()

        ROTA = '/formas-pagamentos/'
        log.info(f"Passará por {len(ids_formas_pagamento)} formas pagamentos")
        for idFormaPagamento in tqdm(ids_formas_pagamento,
                                     desc="Busca formas pag."):
            log.info(f"Solicita dados da forma pag {idFormaPagamento} na API")
            forma_pagamento = solicita_formas_pagamento(
                rota=ROTA+f"{idFormaPagamento}", api=api)

            log.info("Insere formas de pagamento")
            db_inserir_uma_linha(
                tabela=tabela, colunas=colunas, valores=forma_pagamento,
                db=self.db,  conn=conn)

        log.info("Fim de preencher formas de pagamento")

    def preencher_contas_contabeis(self, tabela: str, conn, api):
        """Preenche a tabela contas_contabeis da database."""
        colunas = self.tabelas_colunas[tabela][:]
        contas_contabeis = api.solicita_na_api('/contas-contabeis')['data']

        log.info(f"Passará por {len(contas_contabeis)} contas banarias")
        for c_contabel in tqdm(contas_contabeis, desc="Salva conta_contabeis"):
            c_contabel["id_bling"] = c_contabel.pop("id")
            c_contabel["nome"] = c_contabel.pop("descricao")

            log.info(f"Insere conta {c_contabel['id_bling']} no banco")
            db_inserir_uma_linha(
                tabela=tabela, colunas=colunas, valores=c_contabel,
                db=self.db,  conn=conn)
        log.info("Contas contáveis inseridas")

    def preencher_categorias_receitas_despesas_tipo(self, tabela: str, conn):
        """Preenche a tabela categorias_receitas_despesas_tipo da database."""
        colunas = self.tabelas_colunas[tabela][:]

        valores = [
            {"id": 0, "nome": "Unknow"},
            {"id": 1, "nome": "Despesa"},
            {"id": 2, "nome": "Receita"},
            {"id": 3, "nome": "Receita e despesa"},
            {"id": 4, "nome": "Transferências de entrada"},
            {"id": 5, "nome": "Transferências de saida"},
        ]

        log.info("Insere tipos de categorias")
        db_inserir_varias_linhas(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)
        log.info("Fim de tipos de categorias")

    def preencher_categorias_receitas_despesas(self, tabela: str, conn, api):
        """Preenche a tabela produtos_formatos da database."""
        colunas = self.tabelas_colunas[tabela][:]
        ROTA = "/categorias/receitas-despesas?&tipo=0&situacao=0&"
        ids_categorias = api_pega_todos_id(api, ROTA)
        ids_categorias.sort()

        ROTA = '/categorias/receitas-despesas/'
        log.info(f"Passará por {len(ids_categorias)} categorias")
        list_relacao_categoria = []
        for idCategoria in tqdm(ids_categorias, desc="Busca categorias"):
            log.info(f"Solicita dados da categoria {idCategoria} na API")
            rel, categoria = solicita_categeoria(rota=ROTA+f"{idCategoria}",
                                                 api=api)

            log.info("Insere categoria")
            db_inserir_uma_linha(tabela=tabela, colunas=colunas, db=self.db,
                                 valores=categoria, conn=conn)

            # Pegando informações sobre relação da categoria
            if rel:
                list_relacao_categoria.append(rel)

        log.info(f"Insere {len(list_relacao_categoria)} relacoes de categoria")
        print(f"Insere {len(list_relacao_categoria)} relacoes de categoria")
        tab_relacao = "categorias_receitas_despesas_relacao"
        colunas_relacao = self .tabelas_colunas[tab_relacao][:]
        colunas_relacao.remove("id")
        db_inserir_varias_linhas(tabela=tab_relacao,
                                 colunas=colunas_relacao, conn=conn,
                                 db=self.db, valores=list_relacao_categoria)

        log.info("Termina de inserir categorias receitas despesas")

    def preencher_contas_tipo_ocorrencia(self, tabela: str, conn):
        """Preenche a tabela contas_tipo_ocorrencia da database."""
        colunas = self.tabelas_colunas[tabela][:]

        valores = [
            {"id": 1, "nome": "Única"},
            {"id": 2, "nome": "Parcelada"},
            {"id": 3, "nome": "Mensal"},
            {"id": 4, "nome": "Bimestral"},
            {"id": 5, "nome": "Trimestral"},
            {"id": 6, "nome": "Semestral"},
            {"id": 7, "nome": "Anual"},
            {"id": 8, "nome": "Quinzenal"},
            {"id": 9, "nome": "Semanal"},
        ]

        log.info("Insere tipos de ocorrência de contas")
        db_inserir_varias_linhas(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)
        log.info("Fim de preencher tipos de ocorrência de contas")

    def preencher_vendedores(self, tabela: str, conn, api):
        """Preenche a tabela vendedores da database."""
        colunas = self.tabelas_colunas[tabela][:]
        ids_vendedores = api_pega_todos_id(
            api, "/vendedores?situacaoContato=A&")
        ids_vendedores += api_pega_todos_id(
            api, "/vendedores?situacaoContato=I&")
        ids_vendedores += api_pega_todos_id(
            api, "/vendedores?situacaoContato=S&")
        ids_vendedores += api_pega_todos_id(
            api, "/vendedores?situacaoContato=E&")
        ids_vendedores.sort()

        ROTA = "/vendedores/"
        log.info(f"Passará por {len(ids_vendedores)} vendedores")
        for idVendedor in tqdm(ids_vendedores, desc="Busca vendedores"):
            log.info(f"Solicita vendedor {idVendedor} na API")
            conta = solicita_vendedor(rota=ROTA+f"{idVendedor}", api=api)

            log.info("Insere conta")
            db_inserir_uma_linha(
                tabela=tabela, colunas=colunas, valores=conta,
                db=self.db,  conn=conn)

        log.info("Fim de preencher contas receitas despesas")

    def preencher_contas_receitas_despesas(self, tabela: str, conn, api):
        """Preenche a tabela contas_receitas_despesas da database."""
        colunas = self.tabelas_colunas[tabela][:]
        contas_receber = api_pega_todos_id(api, "/contas/receber?")
        contas_receber.sort()
        contas_pagar = api_pega_todos_id(api, "/contas/pagar?")
        contas_pagar.sort()
        ids_contas = [contas_receber, contas_pagar]

        ROTA = ["/contas/receber/", "/contas/pagar/"]
        for idx in tqdm(range(len(ROTA)), desc="Busca contas", position=0):
            for idConta in tqdm(ids_contas[idx], desc=f"{ROTA[idx]}",
                                leave=True, position=1):
                log.info(f"Solicita dados da conta {idConta} na API")
                conta = solicita_conta(rota=ROTA[idx]+f"{idConta}", api=api)

                log.info("Insere conta")
                db_inserir_uma_linha(
                    tabela=tabela, colunas=colunas, valores=conta,
                    db=self.db,  conn=conn)

        log.info("Fim de preencher contas receitas despesas")

    def preencher_modulo_contas(self, conn, api, fuso):
        """Preencher módulo de contas."""
        log.info("Inicio")

        log.info("Inicio preencher contas_situacao")
        self.preencher_contas_situacao(
            tabela="contas_situacao", conn=conn)

        log.info("Inicio preencher tipos_pagamento")
        self.preencher_tipos_pagamento(tabela="tipos_pagamento", conn=conn)

        log.info("Inicio preencher formas_pagamento_padrao")
        self.preencher_formas_pagamento_padrao(
            tabela="formas_pagamento_padrao", conn=conn)

        log.info("Inicio preencher formas_pagamento_destino")
        self.preencher_formas_pagamento_destino(
            tabela="formas_pagamento_destino", conn=conn)

        log.info("Inicio preencher formas_pagamento_finalidade")
        self.preencher_formas_pagamento_finalidade(
            tabela="formas_pagamento_finalidade", conn=conn)

        log.info("Inicio preencher formas_pagamento")
        self.preencher_formas_pagamento(tabela="formas_pagamento", conn=conn,
                                        api=api)

        log.info("Inicio preencher contas_contabeis")
        self.preencher_contas_contabeis(tabela="contas_contabeis", conn=conn,
                                        api=api)

        log.info("Inicio preenche categorias_receitas_despesas_tipo")
        self.preencher_categorias_receitas_despesas_tipo(
            tabela="categorias_receitas_despesas_tipo", conn=conn)

        log.info("Inicio preencher categorias_receitas_despesas")
        self.preencher_categorias_receitas_despesas(
            tabela="categorias_receitas_despesas", conn=conn, api=api)

        log.info("Inicio preencher contas_tipo_ocorrencia")
        self.preencher_contas_tipo_ocorrencia(tabela="contas_tipo_ocorrencia",
                                              conn=conn)

        log.info("Inicio preencher vendedores")
        self.preencher_vendedores(tabela="vendedores", conn=conn, api=api)

        log.info("Inicio preencher contas_receitas_despesas")
        self.preencher_contas_receitas_despesas(
            tabela="contas_receitas_despesas", conn=conn, api=api)

        log.info("Fim preencher contas")


if __name__ == "__main__":
    pass
