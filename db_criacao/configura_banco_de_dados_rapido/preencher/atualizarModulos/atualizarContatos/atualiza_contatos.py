#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 16:12:39 2024.

@author: vcsil
"""
from atualizarModulos.utils import api_pega_todos_id_verifica_db
from preencherModulos.utils import (
    db_inserir_uma_linha, db_pega_varios_elementos)

from atualizarModulos.atualizarContatos.utils_contatos import (
    _verifica_atualiza_contato)
from tqdm import tqdm
import logging

log = logging.getLogger(__name__)

# =-=-=-=-=-=-=-=-=-=-=-=-= Preencher Tabela Contatos =-=-=-=-=-=-=-=-=-=-=-=-=


class AtualizarContatos():
    """Preenche módulo de contatos."""

    def __init__(self, tabelas_colunas, db):
        self.tabelas_colunas = tabelas_colunas
        self.db = db

    def _atualizar_contatos_situacao(self, tabela: str, sigla, conn):
        """Atualiza a tabela contatos_situacao da database."""
        log.info("Insere nova situação de contatos")
        colunas = self.tabelas_colunas[tabela][:]
        colunas.remove('id')

        valor = {"nome": sigla, "sigla": sigla}

        id_situacao = db_inserir_uma_linha(
            tabela=tabela, colunas=colunas, valores=valor,
            db=self.db, conn=conn)

        return id_situacao

    def _atualizar_contatos_tipo(self, tabela: str, sigla, conn):
        """Atualiza a tabela contatos_tipo da database."""
        log.info("Insere novo tipo de contatos")
        colunas = self.tabelas_colunas[tabela][:]
        colunas.remove('id')

        valor = {"nome": sigla, "sigla": sigla}

        id_tipo = db_inserir_uma_linha(tabela=tabela, colunas=colunas,
                                       valores=valor, db=self.db, conn=conn)
        return id_tipo

    def _atualizar_contatos_indicador_inscricao_estadual(self, tabela: str,
                                                         id_iie, conn):
        """Atualiza a tabela contatos_indicador_inscricao_estadual do db."""
        log.info("Insere novo indicador inscricao ie de contatos")
        colunas = self.tabelas_colunas[tabela][:]

        valor = {"id": id_iie, "nome": str(id_iie)}

        return db_inserir_uma_linha(
            tabela=tabela, colunas=colunas, valores=valor,
            db=self.db, conn=conn)

    def _atualizar_contatos_classificacao(self, tabela: str,
                                          dict_classificacao, conn, api):
        """Atualiza a tabela contatos_classificacao da database."""
        log.info("Insere nova classificacao de contatos na API")
        colunas = self.tabelas_colunas[tabela][:]

        valor = dict_classificacao

        id_classificacao = db_inserir_uma_linha(
            tabela=tabela, colunas=colunas, valores=valor,
            db=self.db, conn=conn)
        return id_classificacao

    def atualiza_contatos(self, tabela: str, conn, api, fuso):
        """Preenche a tabela contatos da database."""
        log.info("Insere novos contatos na API")
        ids_contatos_api = api_pega_todos_id_verifica_db(
            api=api, db=self.db, param='/contatos?criterio=1&',
            tabela_busca="contatos", coluna_busca="id_bling",
            colunas_retorno="id_bling", conn=conn)

        ids_contatos_db = db_pega_varios_elementos(
            tabela_busca='contatos', colunas_retorno="id_bling",
            db=self.db, conn=conn)
        ids_contatos_db = [contato["id_bling"] for contato in ids_contatos_db]

        ids_contatos_novos = list(set(ids_contatos_api) - set(ids_contatos_db))
        ids_contatos_novos.sort()

        t_desc = f"Adciona {len(ids_contatos_novos)} contatos novos"
        for contato_novo in tqdm(ids_contatos_novos, desc=t_desc):
            _verifica_atualiza_contato(
                id_contato=contato_novo, tabelas_colunas=self.tabelas_colunas,
                api=api, db=self.db, conn=conn, fuso=fuso)
            conn.commit()

    def atualizar_modulo_contatos(self, conn, api, fuso):
        """
        Preenche por completo o módulo, chama todas funções necessárias.

        Parameters
        ----------
        conn : TYPE
            Connection com banco de dados.
        api : TYPE
            Módulo que manipula a API.
        fuso : TYPE
            Fuso horário do sistema.
        """
        log.info("Começa atualizar contatos.")

        log.info("Atualiza contatos")
        self.atualiza_contatos(tabela='contatos', conn=conn, api=api,
                               fuso=fuso)

        log.info("Fim contatos")


if __name__ == "__main__":
    pass
