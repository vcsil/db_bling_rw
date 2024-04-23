#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 11:36:38 2023.

@author: vcsil
"""

from preencherModulos.preencherContatos.utils_contatos import (
    manipula_dados_contatos, regra_pais)
from preencherModulos.utils import (
    db_inserir_varias_linhas, api_pega_todos_id, possui_informacao,
    db_inserir_uma_linha, verifica_preenche_valor, manipula_dados_endereco)

from config.constants import API, TABELAS_COLUNAS
from typing import Dict, Union
from tqdm import tqdm
import logging

log = logging.getLogger("root")

# =-=-=-=-=-=-=-=-=-=-=-=-= Preencher Tabela Contatos =-=-=-=-=-=-=-=-=-=-=-=-=


class PreencherContatos():
    """Preenche módulo de contatos."""

    def __init__(self):
        pass

    def preencher_contatos_situacao(self, conn):
        """Preenche a tabela contatos_situacao da database."""
        tabela = "contatos_situacao"
        colunas = TABELAS_COLUNAS[tabela][:]
        colunas.remove("id")

        valores = [
            {"nome": "Ativo", "sigla": "A"},
            {"nome": "Excluído", "sigla": "E"},
            {"nome": "Inativo", "sigla": "I"},
            {"nome": "Sem movimentação", "sigla": "S"},
        ]

        log.info("Insere situação de contatos")
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Situações de contatos inseridas")

    def preencher_contatos_tipo(self, conn):
        """Preenche a tabela contatos_tipo da database."""
        tabela = "contatos_tipo"
        colunas = TABELAS_COLUNAS[tabela][:]
        colunas.remove("id")

        valores = [
            {"nome": "Jurídica", "sigla": "J"},
            {"nome": "Física", "sigla": "F"},
            {"nome": "Estrangeira", "sigla": "E"},
        ]

        log.info("Insere tipos de contatos")
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Tipos de contatos inseridos")

    def preencher_contatos_indicador_inscricao_estadual(self, conn):
        """Preenche a tabela contatos_indicador_inscricao_estadual do db."""
        tabela = "contatos_indicador_inscricao_estadual"
        colunas = TABELAS_COLUNAS[tabela][:]

        nome2 = "Contribuinte isento de Inscrição no cadastro de Contribuintes"
        valores = [
            {"id": 1, "nome": "Contribuinte ICMS"},
            {"id": 2, "nome": nome2},
            {"id": 9, "nome": "Não Contribuinte"},
        ]

        log.info("Insere indicador inscricao ie de contatos")
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Indicadores de inscrição de ie inseridos")

    def preencher_contatos_classificacao(self, conn):
        """Preenche a tabela contatos_classificacao da database."""
        tabela = "contatos_classificacao"
        colunas = TABELAS_COLUNAS[tabela][:]

        log.info("Busca classificacao de contatos na API")
        ROTA = "/contatos/tipos"
        contatos_classificacao = API.solicita_na_api(ROTA)

        valores = contatos_classificacao["data"]
        valores = [{"id_bling": classi["id"], "nome": classi["descricao"]}
                   for classi in valores]

        log.info("Insere classificacao de contatos")
        db_inserir_varias_linhas(tabela, colunas, valores, conn)
        log.info("Classificação de contatos inseridos")

    def preencher_contatos(self, conn, unicoContatoNovo=[]):
        """Preenche a tabela contatos da database."""
        if unicoContatoNovo:
            id_contatos = unicoContatoNovo[:]
        else:
            id_contatos = api_pega_todos_id("/contatos?criterio=1&")
            id_contatos.sort()

        tabela = "contatos"
        colunas = TABELAS_COLUNAS[tabela][:]

        ROTA = "/contatos/"
        log.info(f"Passará por {len(id_contatos)} contatos")
        for idContato in tqdm(id_contatos, desc="Inserindo contatos"):
            log.info(f"Solicita dados do contato {idContato} na API")
            contato = API.solicita_na_api(ROTA+f"{idContato}")["data"]
            # Pegando informações sobre o contato
            log.info("Manipula dados dos contatos")
            contato_info = manipula_dados_contatos(contato, conn)

            # Pegando informações referente ao endereço
            contato_endereco = {
                "id_contato": contato["id"],
                "endereco": contato["endereco"],
                "pais": contato["pais"],
                "tipo": contato["tipo"]
            }

            log.info("Insere contato")
            db_inserir_uma_linha("contatos", colunas, contato_info, conn)
            self.preencher_endereco(conn, contato_endereco)

        log.info("Todos contatos inseridos")

    def preencher_endereco(
            self,
            conn,
            dict_endereco: Dict[str,
                                Union[str,
                                      Dict[str,
                                           Union[str,
                                                 Dict[str, Dict[str, str]]]]]]
    ):
        """Preenche campos referentes ao endereço."""
        log.info("Insere endereco de contatos")
        pais = regra_pais(dict_endereco["tipo"], dict_endereco["pais"]["nome"])

        list_colunas = TABELAS_COLUNAS["endereco_paises"]
        for tipo_endereco in dict_endereco["endereco"].keys():
            endereco = dict_endereco["endereco"][tipo_endereco]
            if tipo_endereco == "geral":
                id_tipo_endereco = 0
            elif tipo_endereco == "cobranca":
                id_tipo_endereco = 1

            if possui_informacao(endereco):
                id_pais = verifica_preenche_valor("endereco_paises", "nome",
                                                  pais, list_colunas, conn)

                endereco = manipula_dados_endereco(endereco, id_pais, conn)

                # Inserir na tabela enderecos
                valores = list(endereco.values())
                colunas = list(endereco.keys())
                list_colunas_end = ["id"]+colunas
                id_endereco = verifica_preenche_valor("enderecos", colunas,
                                                      valores,
                                                      list_colunas_end, conn)

                colunas_enderecos_inserido = (
                    TABELAS_COLUNAS["contatos_enderecos"][:])
                colunas_enderecos_inserido.remove("id")
                valores = {
                    "id_contato": dict_endereco["id_contato"],
                    "id_endereco": id_endereco,
                    "tipo_endereco": id_tipo_endereco
                }
                # Inserir na tabela contatos_enderecos
                db_inserir_uma_linha("contatos_enderecos",
                                     colunas_enderecos_inserido, valores, conn)

        log.info("Endereço inserido")

    def preencher_modulo_contatos(self, conn):
        """
        Preenche por completo o módulo, chama todas funções necessárias.

        Parameters
        ----------
        conn : TYPE
            Connection com banco de dados.
        """
        log.info("Começa preencher contatos.")
        # with conn.transaction():
        log.info("Preencher contatos_situacao")
        self.preencher_contatos_situacao(conn)

        log.info("Preencher contatos_tipo")
        self.preencher_contatos_tipo(conn)

        log.info("Preencher contatos_indicador_inscricao")
        self.preencher_contatos_indicador_inscricao_estadual(conn)

        log.info("Preencher contatos_classificacao")
        self.preencher_contatos_classificacao(conn)

        log.info("Preencher contatos")
        self.preencher_contatos(conn)

        log.info("Fim contatos")


if __name__ == "__main__":
    pass
