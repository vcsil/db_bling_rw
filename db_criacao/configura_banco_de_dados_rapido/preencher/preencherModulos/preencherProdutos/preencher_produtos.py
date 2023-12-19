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

    def preencher_produtos_tipos(self):
        """Preenche a tabela produtos_tipos da database."""
        pass

    def preencher_produtos_formatos(self):
        """Preenche a tabela produtos_formatos da database."""
        pass

    def preencher_produtos_tipo_producao(self):
        """Preenche a tabela produtos_formatos da database."""
        pass

    def preencher_produtos_condicao(self):
        """Preenche a tabela produtos_formatos da database."""
        pass

    def preencher_produtos_categorias(self):
        """Preenche a tabela produtos_formatos da database."""
        pass
