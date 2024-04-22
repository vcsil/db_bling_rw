#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 16:12:39 2024.

@author: vcsil
"""
from preencherModulos.utils import (db_inserir_uma_linha,
                                    db_inserir_varias_linhas)

from atualizarModulos.utils import (solicita_novos_ids, solicita_item_novos,
                                    txt_fundo_verde)
from atualizarModulos.atualizarContatos.utils_contatos import (
    _verifica_atualiza_contato)

from config.constants import TABELAS_COLUNAS
from tqdm import tqdm
import logging

log = logging.getLogger("root")

# =-=-=-=-=-=-=-=-=-=-=-=-= Preencher Tabela Contatos =-=-=-=-=-=-=-=-=-=-=-=-=


class AtualizarContatos():
    """Preenche módulo de contatos."""

    def __init__(self):
        pass

    def _atualizar_contatos_situacao(self, tabela: str, sigla, conn):
        """Atualiza a tabela contatos_situacao da database."""
        log.info("Insere nova situação de contatos")
        colunas = TABELAS_COLUNAS[tabela][:]
        colunas.remove("id")

        valor = {"nome": sigla, "sigla": sigla}

        id_situacao = db_inserir_uma_linha(tabela, colunas, valor, conn)

        return id_situacao

    def _atualizar_contatos_tipo(self, tabela: str, sigla, conn):
        """Atualiza a tabela contatos_tipo da database."""
        log.info("Insere novo tipo de contatos")
        colunas = TABELAS_COLUNAS[tabela][:]
        colunas.remove("id")

        valor = {"nome": sigla, "sigla": sigla}

        id_tipo = db_inserir_uma_linha(tabela, colunas, valor, conn)
        return id_tipo

    def _atualizar_contatos_indicador_inscricao_estadual(self, tabela: str,
                                                         id_iie, conn):
        """Atualiza a tabela contatos_indicador_inscricao_estadual do db."""
        log.info("Insere novo indicador inscricao ie de contatos")
        colunas = TABELAS_COLUNAS[tabela][:]

        valor = {"id": id_iie, "nome": str(id_iie)}

        return db_inserir_uma_linha(tabela, colunas, valor, conn)

    def atualizar_contatos_classificacao(self, conn):
        """Atualiza a tabela contatos_classificacao da database."""
        log.info("Insere nova classificacao de contatos na API")
        tabela = "contatos_classificacao"
        colunas = TABELAS_COLUNAS[tabela][:]

        PARAM = "/contatos/tipos"
        valores = solicita_item_novos(PARAM, tabela, "id_bling", conn)

        if len(valores) == 0:
            return

        txt_fundo_verde(f"Insere {len(valores)} categ. novas")
        valores = [{"id_bling": classi["id"], "nome": classi["descricao"]}
                   for classi in valores]

        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        return

    def atualiza_contatos(self, conn):
        """Preenche a tabela contatos da database."""
        log.info("Insere novos contatos na API")
        tabela = "contatos"

        PARAM = "/contatos?criterio=3&"
        ids_contatos_novos = solicita_novos_ids(PARAM, tabela, "id_bling",
                                                conn)

        if len(ids_contatos_novos) == 0:
            return

        txt_fundo_verde(f"Adciona {len(ids_contatos_novos)} contatos novos")
        t_desc = f"Adciona {len(ids_contatos_novos)} contatos novos"
        for id_contato_novo in tqdm(ids_contatos_novos, desc=t_desc):
            _verifica_atualiza_contato(id_contato_novo, conn)
            conn.commit()
        return

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
