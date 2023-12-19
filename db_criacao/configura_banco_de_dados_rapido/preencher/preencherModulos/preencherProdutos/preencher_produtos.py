#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 13:06:07 2023.

@author: vcsil
"""
from config.conexao_db import ConectaDB

import logging

log = logging.getLogger(__name__)

# =-=-=-=-=-=-=-=-=-=-=-=-= Preencher Tabela Contatos =-=-=-=-=-=-=-=-=-=-=-=-=


class PreencherPrdutos(ConectaDB):
    """Preenche módulo de produtos."""

    def __init__(self, tabelas_colunas):
        self.tabelas_colunas = tabelas_colunas

    def preencher_produtos_tipos(self, tabela: str, conn):
        """Preenche a tabela produtos_tipos da database."""
        colunas = self.tabelas_colunas[tabela][:]
        colunas.remove('id')

        valores = [
            {"nome": 'Serviço', "sigla": 'S'},
            {"nome": 'Produto', "sigla": 'P'},
            {"nome": 'Serviço 06 21 22', "sigla": 'N'},
        ]

        log.info("Insere tipos de contatos")
        self.insert_many_in_db(
            tabela=tabela, colunas=colunas, valores=valores,
            valores_placeholder=colunas, conn=conn)
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
        self.insert_many_in_db(
            tabela=tabela, colunas=colunas, valores=valores,
            valores_placeholder=colunas, conn=conn)
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
        self.insert_many_in_db(
            tabela=tabela, colunas=colunas, valores=valores,
            valores_placeholder=colunas, conn=conn)
        log.info("Fim")

    def preencher_produtos_condicao(self):
        """Preenche a tabela produtos_formatos da database."""
        pass

    def preencher_produtos_categorias(self):
        """Preenche a tabela produtos_formatos da database."""
        pass
