#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 16:12:39 2024.

@author: vcsil
"""
from preencherModulos.utils import (
    db_inserir_uma_linha, db_inserir_varias_linhas)

from atualizarModulos.utils import solicita_novos_ids, solicita_item_novos
from atualizarModulos.atualizarContatos.utils_contatos import (
    _verifica_atualiza_contato)

from config.constants import DB, TABELA_COLUNAS
from colorama import Back, Style
from tqdm import tqdm
import logging

log = logging.getLogger('root')

# =-=-=-=-=-=-=-=-=-=-=-=-= Preencher Tabela Contatos =-=-=-=-=-=-=-=-=-=-=-=-=


class AtualizarContatos():
    """Preenche módulo de contatos."""

    def __init__(self):
        pass

    def _atualizar_contatos_situacao(self, tabela: str, sigla, conn):
        """Atualiza a tabela contatos_situacao da database."""
        log.info("Insere nova situação de contatos")
        colunas = TABELA_COLUNAS[tabela][:]
        colunas.remove('id')

        valor = {"nome": sigla, "sigla": sigla}

        id_situacao = db_inserir_uma_linha(tabela=tabela, colunas=colunas,
                                           valores=valor, db=DB, conn=conn)

        return id_situacao

    def _atualizar_contatos_tipo(self, tabela: str, sigla, conn):
        """Atualiza a tabela contatos_tipo da database."""
        log.info("Insere novo tipo de contatos")
        colunas = TABELA_COLUNAS[tabela][:]
        colunas.remove('id')

        valor = {"nome": sigla, "sigla": sigla}

        id_tipo = db_inserir_uma_linha(tabela=tabela, colunas=colunas,
                                       valores=valor, db=DB, conn=conn)
        return id_tipo

    def _atualizar_contatos_indicador_inscricao_estadual(self, tabela: str,
                                                         id_iie, conn):
        """Atualiza a tabela contatos_indicador_inscricao_estadual do db."""
        log.info("Insere novo indicador inscricao ie de contatos")
        colunas = TABELA_COLUNAS[tabela][:]

        valor = {"id": id_iie, "nome": str(id_iie)}

        return db_inserir_uma_linha(tabela=tabela, colunas=colunas,
                                    valores=valor, db=DB, conn=conn)

    def atualizar_contatos_classificacao(self, conn):
        """Atualiza a tabela contatos_classificacao da database."""
        log.info("Insere nova classificacao de contatos na API")
        tabela = 'contatos_classificacao'
        colunas = TABELA_COLUNAS[tabela][:]

        PARAM = "/contatos/tipos"
        valores = solicita_item_novos(param=PARAM, tabela=tabela, conn=conn,
                                      colunas_retorno="id_bling")

        if len(valores) == 0:
            return

        print(Back.GREEN + f"Insere {len(valores)} categ. novas"
              + Style.RESET_ALL)
        valores = [{"id_bling": classi["id"], "nome": classi["descricao"]}
                   for classi in valores]

        db_inserir_varias_linhas(tabela=tabela, colunas=colunas,
                                 valores=valores, db=DB, conn=conn)

    def atualiza_contatos(self, conn):
        """Preenche a tabela contatos da database."""
        log.info("Insere novos contatos na API")
        tabela = 'contatos'

        ids_contatos_novos = solicita_novos_ids(
            param="/contatos?criterio=3&", tabela_busca="contatos", conn=conn,
            coluna_busca="id_bling", coluna_retorno="id_bling")

        if len(ids_contatos_novos) == 0:
            return

        print(Back.GREEN + f"Adciona {len(ids_contatos_novos)} contatos novos"
              + Style.RESET_ALL)
        t_desc = f"Adciona {len(ids_contatos_novos)} contatos novos"
        for contato_novo in tqdm(ids_contatos_novos, desc=t_desc):
            _verifica_atualiza_contato(id_contato=contato_novo, conn=conn,
                                       tabelas_colunas=TABELA_COLUNAS)
            conn.commit()

    def atualizar_modulo_contatos(self, conn):
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

        log.info("Atualiza contatos_classificacao")
        self.atualizar_contatos_classificacao(conn=conn)

        log.info("Atualiza contatos")
        self.atualiza_contatos(conn=conn)

        log.info("Fim contatos")


if __name__ == "__main__":
    pass
