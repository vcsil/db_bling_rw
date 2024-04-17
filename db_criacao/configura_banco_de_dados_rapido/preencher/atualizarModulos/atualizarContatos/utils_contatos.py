#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 16:22:17 2024.

@author: vcsil
"""
from atualizarModulos.utils import db_verifica_se_existe
from config.constants import FUSO, API, DB, TABELAS_COLUNAS


def _verifica_atualiza_contato(id_contato, conn):
    tabela = "contatos"
    coluna = "id_bling"
    contato_exite = db_verifica_se_existe(tabela, coluna, [id_contato], conn)

    if contato_exite:
        return
    else:
        from preencherModulos.preencherContatos.preencher_contatos import (
            PreencherContatos)

        PreencherContatos(TABELAS_COLUNAS, DB).preencher_contatos(
            tabela, conn, API, FUSO, unicoContatoNovo=[id_contato])

        return


if __name__ == "__main__":
    pass
