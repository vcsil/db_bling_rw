#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 19:01:03 2024.

@author: vcsil
"""
from preencherModulos.preencherContas.utils_contas import (
    solicita_formas_pagamento, solicita_categeoria, solicita_conta,
    solicita_vendedor, _manipula_bordero)
from preencherModulos.utils import (
    db_inserir_varias_linhas, api_pega_todos_id, db_inserir_uma_linha)
from config.constants import API, TABELAS_COLUNAS

from tqdm import tqdm
import logging

log = logging.getLogger("root")

# =-=-=-=-=-=-=-=-=-=-=-=-=- Preencher Tabela Contas =-=-=-=-=-=-=-=-=-=-=-=-=-


class PreencherContas():
    """Preenche módulo de contas."""

    def __init__(self):
        pass

    def preencher_contas_situacao(self, conn):
        """Preenche a tabela contas_situacao da database."""
        tabela = "contas_situacao"
        colunas = TABELAS_COLUNAS[tabela][:]

        valores = [
            {"id": 1, "nome": "Em aberto"},
            {"id": 2, "nome": "Recebido"},
            {"id": 3, "nome": "Parcialmente recebido"},
            {"id": 4, "nome": "Devolvido"},
            {"id": 5, "nome": "Cancelado"},
        ]

        log.info("Insere situação contas receber")
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Fim de preencher situação contas receber")

    def preencher_tipos_pagamento(self, conn):
        """Preenche a tabela produtos_tipos da database."""
        tabela = "tipos_pagamento"
        colunas = TABELAS_COLUNAS[tabela][:]

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
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Fim de preencher tipos de pagamento")

    def preencher_formas_pagamento_padrao(self, conn):
        """Preenche a tabela formas_pagamento_padrao da database."""
        tabela = "formas_pagamento_padrao"
        colunas = TABELAS_COLUNAS[tabela][:]

        valores = [
            {"id": 0, "nome": "Não"},
            {"id": 1, "nome": "Padrão"},
            {"id": 2, "nome": "Padrão devolução"},
        ]

        log.info("Insere padrões de pagamento")
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Fim de preencher padrões de pagamento")

    def preencher_formas_pagamento_destino(self, conn):
        """Preenche a tabela formas_pagamento_destino da database."""
        tabela = "formas_pagamento_destino"
        colunas = TABELAS_COLUNAS[tabela][:]

        valores = [
            {"id": 1, "nome": "Conta a receber/pagar"},
            {"id": 2, "nome": "Ficha financeira"},
            {"id": 3, "nome": "Caixa e bancos"},
        ]

        log.info("Insere destino de pagamento")
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Fim de preencher destino de pagamento")

    def preencher_formas_pagamento_finalidade(self, conn):
        """Preenche a tabela formas_pagamento_finalidade da database."""
        tabela = "formas_pagamento_finalidade"
        colunas = TABELAS_COLUNAS[tabela][:]

        valores = [
            {"id": 1, "nome": "Pagamentos"},
            {"id": 2, "nome": "Recebimentos"},
            {"id": 3, "nome": "Pagamentos e Recebimentos"},
        ]

        log.info("Insere finalidade de pagamento")
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Fim de preencher finalidade de pagamento")

    def preencher_formas_pagamento(self, conn):
        """Preenche a tabela formas_pagamento da database."""
        tabela = "formas_pagamento"
        colunas = TABELAS_COLUNAS[tabela][:]
        ids_formas_pagamento = api_pega_todos_id("/formas-pagamentos?")
        ids_formas_pagamento.sort()

        ROTA = "/formas-pagamentos/"
        log.info(f"Passará por {len(ids_formas_pagamento)} formas pagamentos")
        for id_fp in tqdm(ids_formas_pagamento, desc="Busca formas pag.",
                          position=1):
            log.info(f"Solicita dados da forma pag {id_fp} na API")
            forma_pagamento = solicita_formas_pagamento(ROTA+f"{id_fp}")

            log.info("Insere formas de pagamento")
            db_inserir_uma_linha(tabela, colunas, forma_pagamento, conn)

        log.info("Fim de preencher formas de pagamento")

    def preencher_contas_contabeis(self, conn):
        """Preenche a tabela contas_contabeis da database."""
        tabela = "contas_contabeis"
        colunas = TABELAS_COLUNAS[tabela][:]
        contas_contabeis = API.solicita_na_api("/contas-contabeis")["data"]

        log.info(f"Passará por {len(contas_contabeis)} contas banarias")
        for c_contabel in tqdm(contas_contabeis, desc="Salva conta_contabeis",
                               position=1):
            c_contabel["id_bling"] = c_contabel.pop("id")
            c_contabel["nome"] = c_contabel.pop("descricao")

            log.info(f"Insere conta {c_contabel['id_bling']} no banco")
            db_inserir_uma_linha(tabela, colunas, c_contabel, conn)
        log.info("Contas contáveis inseridas")

    def preencher_categorias_receitas_despesas_tipo(self, conn):
        """Preenche a tabela categorias_receitas_despesas_tipo da database."""
        tabela = "categorias_receitas_despesas_tipo"
        colunas = TABELAS_COLUNAS[tabela][:]

        valores = [
            {"id": 0, "nome": "Unknow"},
            {"id": 1, "nome": "Despesa"},
            {"id": 2, "nome": "Receita"},
            {"id": 3, "nome": "Receita e despesa"},
            {"id": 4, "nome": "Transferências de entrada"},
            {"id": 5, "nome": "Transferências de saida"},
        ]

        log.info("Insere tipos de categorias")
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Fim de tipos de categorias")

    def preencher_categorias_receitas_despesas(self, conn):
        """Preenche a tabela produtos_formatos da database."""
        tabela = "categorias_receitas_despesas"
        colunas = TABELAS_COLUNAS[tabela][:]
        ROTA = "/categorias/receitas-despesas?&tipo=0&situacao=0&"
        ids_categorias = api_pega_todos_id(ROTA)
        ids_categorias.sort()

        ROTA = "/categorias/receitas-despesas/"
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

        # Adiciona id 0
        id0 = {"id_bling": 0, "nome": "Unknow", "id_tipo": 0, "situacao": True}
        db_inserir_uma_linha(tabela, colunas, id0, conn)

        log.info(f"Insere {len(list_relacao_categoria)} relacoes de categoria")
        print(f"Insere {len(list_relacao_categoria)} relacoes de categoria")

        tab_relacao = "categorias_receitas_despesas_relacao"
        colunas_relacao = TABELAS_COLUNAS[tab_relacao][:]
        colunas_relacao.remove("id")
        db_inserir_varias_linhas(tab_relacao, colunas_relacao,
                                 list_relacao_categoria, conn)

        log.info("Termina de inserir categorias receitas despesas")

    def preencher_contas_tipo_ocorrencia(self, conn):
        """Preenche a tabela contas_tipo_ocorrencia da database."""
        tabela = "contas_tipo_ocorrencia"
        colunas = TABELAS_COLUNAS[tabela][:]

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
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Fim de preencher tipos de ocorrência de contas")

    def preencher_vendedores(self, conn):
        """Preenche a tabela vendedores da database."""
        tabela = "vendedores"
        colunas = TABELAS_COLUNAS[tabela][:]
        ids_vendedores = api_pega_todos_id("/vendedores?situacaoContato=A&")
        ids_vendedores += api_pega_todos_id("/vendedores?situacaoContato=I&")
        ids_vendedores += api_pega_todos_id("/vendedores?situacaoContato=S&")
        ids_vendedores += api_pega_todos_id("/vendedores?situacaoContato=E&")
        ids_vendedores = list(set(ids_vendedores))
        ids_vendedores.sort()

        ROTA = "/vendedores/"
        log.info(f"Passará por {len(ids_vendedores)} vendedores")
        for idVendedor in tqdm(ids_vendedores, desc="Busca vendedores",
                               position=1):
            log.info(f"Solicita vendedor {idVendedor} na API")
            conta = solicita_vendedor(rota=ROTA+f"{idVendedor}")

            log.info("Insere conta")
            db_inserir_uma_linha(tabela, colunas, conta, conn)

        log.info("Fim de preencher contas receitas despesas")

    def preencher_contas_receitas_despesas(self, conn):
        """Preenche a tabela contas_receitas_despesas da database."""
        tabela = "contas_receitas_despesas"
        colunas = TABELAS_COLUNAS[tabela][:]
        contas_receber = api_pega_todos_id("/contas/receber?")
        contas_receber.sort()
        contas_pagar = api_pega_todos_id("/contas/pagar?")
        contas_pagar.sort()
        ids_contas = [contas_receber, contas_pagar]

        ROTA = ["/contas/receber/", "/contas/pagar/"]
        for idx in tqdm(range(len(ROTA)), desc="Busca contas", position=0):
            for idConta in tqdm(ids_contas[idx], desc=f"{ROTA[idx]}",
                                leave=True, position=1):
                log.info(f"Solicita dados da conta {idConta} na API")
                conta, borderos = solicita_conta(ROTA[idx]+f"{idConta}", conn)

                log.info("Insere conta")
                db_inserir_uma_linha(tabela, colunas, conta, conn)

                log.info("Insere bordero")
                _manipula_bordero(borderos, conta["id_bling"], conn)
            conn.commit()

        log.info("Fim de preencher contas receitas despesas")

    def preencher_modulo_contas(self, conn):
        """Preencher módulo de contas."""
        log.info("Inicio")

        log.info("Inicio preencher contas_situacao")
        self.preencher_contas_situacao(conn)

        log.info("Inicio preencher tipos_pagamento")
        self.preencher_tipos_pagamento(conn)

        log.info("Inicio preencher formas_pagamento_padrao")
        self.preencher_formas_pagamento_padrao(conn)

        log.info("Inicio preencher formas_pagamento_destino")
        self.preencher_formas_pagamento_destino(conn)

        log.info("Inicio preencher formas_pagamento_finalidade")
        self.preencher_formas_pagamento_finalidade(conn)

        log.info("Inicio preencher formas_pagamento")
        self.preencher_formas_pagamento(conn)

        log.info("Inicio preencher contas_contabeis")
        self.preencher_contas_contabeis(conn)

        log.info("Inicio preenche categorias_receitas_despesas_tipo")
        self.preencher_categorias_receitas_despesas_tipo(conn)

        log.info("Inicio preencher categorias_receitas_despesas")
        self.preencher_categorias_receitas_despesas(conn)

        log.info("Inicio preencher contas_tipo_ocorrencia")
        self.preencher_contas_tipo_ocorrencia(conn)

        log.info("Inicio preencher vendedores")
        self.preencher_vendedores(conn)
        conn.commit()

        log.info("Inicio preencher contas_receitas_despesas")
        self.preencher_contas_receitas_despesas(conn)

        log.info("Fim preencher contas")


if __name__ == "__main__":
    pass
