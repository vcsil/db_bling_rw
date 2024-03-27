#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 16:22:17 2024.

@author: vcsil
"""
from atualizarModulos.utils import db_verifica_se_existe


def _verifica_atualiza_contato(id_contato, tabelas_colunas, api, db, conn,
                               fuso):
    contato_exite = db_verifica_se_existe(
        tabela_busca="contatos", coluna_busca="id_bling", db=db,
        valor_busca=[id_contato], colunas_retorno="id_bling", conn=conn)

    if contato_exite:
        return
    else:
        from preencherModulos.preencherContatos.preencher_contatos import (
            PreencherContatos)

        PreencherContatos(tabelas_colunas, db).preencher_contatos(
            tabela="contatos", conn=conn, api=api, fuso=fuso,
            unicoContatoNovo=[id_contato])

        return


if __name__ == "__main__":
    pass
