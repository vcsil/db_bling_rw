#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 19:03:30 2024.

@author: vcsil
"""
from preencherModulos.utils import (
    db_inserir_uma_linha, db_inserir_varias_linhas, api_pega_todos_id)
from preencherModulos.preencherPedidosVendas.utils_vendas import (
    solicita_preenche_venda)

from config.constants import API, TABELAS_COLUNAS
from tqdm import tqdm
import logging

log = logging.getLogger("root")

# =-=-=-=-=-=-=-=-=-=-=-=-= Preencher Tabela Contatos =-=-=-=-=-=-=-=-=-=-=-=-=


class PreencherVendas():
    """Preenche módulo de produtos."""

    def __init__(self):
        pass

    def preencher_modulos(self, conn):
        """Preenche a tabela modulo da database."""
        tabela = "modulos"
        colunas = TABELAS_COLUNAS[tabela][:]
        modulos = API.solicita_na_api("/situacoes/modulos")["data"]
        list_ids_modulos = []

        log.info(f"Passará por {len(modulos)} módulos")
        for modulo in tqdm(modulos, desc="Salva modulos", position=1):
            modulo["id_bling"] = modulo.pop("id")
            modulo["criar_situacoes"] = modulo.pop("criarSituacoes")
            list_ids_modulos.append(modulo["id_bling"])

            log.info(f"Insere módulo {modulo['id_bling']} no banco de dados")
            db_inserir_uma_linha(tabela, colunas, modulo, conn)
        log.info("Módulos inseridos")
        return list_ids_modulos

    def preencher_situacoes(self, ids_modulos: list, conn):
        """Preenche a tabela situacoes da database."""
        tabela = "situacoes"
        colunas = TABELAS_COLUNAS[tabela][:]

        log.info(f"Passará por {len(ids_modulos)} módulos")
        for id_modulo in tqdm(ids_modulos, desc="Modulo", position=1):
            situacoes = API.solicita_na_api(f"/situacoes/modulos/{id_modulo}")
            situacoes = situacoes["data"]

            log.info(f"Passará por {len(situacoes)} situações")
            for situacao in situacoes:
                situacao["id_bling"] = situacao.pop("id")
                situacao["id_modulo"] = id_modulo
                situacao.pop("idHerdado")

                log.info(f"Insere situacao {situacao['id_bling']}")
                db_inserir_uma_linha(tabela, colunas, situacao, conn)
        log.info("Situações inseridas")

    def preencher_transporte_frete_por_conta_de(self, conn):
        """Preenche a tabela produtos_formatos da database."""
        tabela = "transporte_frete_por_conta_de"
        colunas = TABELAS_COLUNAS[tabela][:]

        valores = [
            {"id": "0",
             "nome": "Contratação do Frete por conta do Remetente (CIF) "},
            {"id": "1",
             "nome": "Contratação do Frete por conta do Destinatário (FOB)"},
            {"id": "2", "nome": "Contratação do Frete por conta de Terceiros"},
            {"id": "3", "nome": "Transporte Próprio por conta do Remetente"},
            {"id": "4",
             "nome": "Transporte Próprio por conta do Destinatário"},
            {"id": "9", "nome": "Sem Ocorrência de Transporte"},
        ]

        log.info("Insere transporte frete por conta de")
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Termina de inserir transporte frete por conta de")

    def preencher_pedidos_vendas(self, conn):
        """Preenche a tabela vendas da database."""
        ids_vendas = api_pega_todos_id("/pedidos/vendas?")
        ids_vendas.sort()

        ROTA = "/pedidos/vendas/"
        for idVenda in tqdm(ids_vendas, desc="Busca pedidos de vendas",
                            position=1):
            log.info(f"Solicita dados da venda {idVenda} na API")
            solicita_preenche_venda(rota=ROTA+f"{idVenda}", conn=conn)

        log.info("Fim de preencher pedido de venda")

    def preencher_modulo_vendas(self, conn):
        """Preencher módulo de produtos."""
        log.info("Inicio preenchimento vendas")

        log.info("Inicio preencher modulos")
        modulos = self.preencher_modulos(conn)

        log.info("Inicio preencher situações")
        self.preencher_situacoes(modulos, conn)

        log.info("Inicio preencher transporte_frete_por_conta_de")
        self.preencher_transporte_frete_por_conta_de(conn)

        log.info("Inicio preencher vendas")
        self.preencher_pedidos_vendas(conn)

        log.info("Fim produtos")


if __name__ == "__main__":
    pass
