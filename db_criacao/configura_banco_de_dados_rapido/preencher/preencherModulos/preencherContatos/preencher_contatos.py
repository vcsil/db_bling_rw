#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 11:36:38 2023.

@author: vcsil
"""

from preencherModulos.preencherContatos.utils_contatos import (UtilsContatos
                                                               as ut_contatos)
from preencherModulos.utils import Utils
from config.conexao_db import ConectaDB

from typing import Dict, Union
from tqdm import tqdm
import logging

log = logging.getLogger(__name__)

# =-=-=-=-=-=-=-=-=-=-=-=-= Preencher Tabela Contatos =-=-=-=-=-=-=-=-=-=-=-=-=


class PreencherContatos(ConectaDB):
    """Preenche módulo de contatos."""

    def __init__(self, tabelas_colunas):
        self.tabelas_colunas = tabelas_colunas

    def preencher_contatos_situacao(self, tabela: str, conn):
        """Preenche a tabela contatos_situacao da database."""
        colunas = self.tabelas_colunas[tabela][:]
        colunas.remove('id')

        valores = [
            {"nome": 'Ativo', "sigla": 'A'},
            {"nome": 'Excluído', "sigla": 'E'},
            {"nome": 'Inativo', "sigla": 'I'},
            {"nome": 'Sem movimentação', "sigla": 'S'},
        ]

        log.info("Insere situacao de contatos")
        self.insert_many_in_db(
            tabela=tabela, colunas=colunas, valores=valores,
            valores_placeholder=colunas, conn=conn)
        log.info("Fim")

    def preencher_contatos_tipo(self, tabela: str, conn):
        """Preenche a tabela contatos_tipo da database."""
        colunas = self.tabelas_colunas[tabela][:]
        colunas.remove('id')

        valores = [
            {"nome": 'Jurídica', "sigla": 'J'},
            {"nome": 'Física', "sigla": 'F'},
            {"nome": 'Estrangeira', "sigla": 'E'},
        ]

        log.info("Insere tipos de contatos")
        self.insert_many_in_db(
            tabela=tabela, colunas=colunas, valores=valores,
            valores_placeholder=colunas, conn=conn)
        log.info("Fim")

    def preencher_contatos_indicador_inscricao_estadual(self, tabela: str,
                                                        conn):
        """Preenche a tabela contatos_indicador_inscricao_estadual do db."""
        colunas = (
            self.tabelas_colunas[tabela][:])
        nome2 = 'Contribuinte isento de Inscrição no cadastro de Contribuintes'
        valores = [
            {"id": 1, "nome": 'Contribuinte ICMS'},
            {"id": 2, "nome": nome2},
            {"id": 9, "nome": 'Não Contribuinte'},
        ]

        log.info("Insere indicador inscricao ie de contatos")
        self.insert_many_in_db(
            tabela=tabela, colunas=colunas, valores=valores,
            valores_placeholder=colunas, conn=conn)
        log.info("Fim")

    def preencher_contatos_classificacao(self, tabela: str, conn, api):
        """Preenche a tabela contatos_classificacao da database."""
        colunas = self.tabelas_colunas[tabela][:]

        ROTA = '/contatos/tipos'
        log.info("Busca classificacao de contatos na API")
        contatos_classificacao = api.solicita_na_api(ROTA)

        valores = contatos_classificacao['data']

        log.info("Insere classificacao de contatos")
        self.insert_many_in_db(
            tabela=tabela, colunas=colunas, valores=valores,
            valores_placeholder=valores[0].keys(), conn=conn)
        log.info("Fim")

    def preencher_contatos(self, tabela: str, conn, api, fuso):
        """Preenche a tabela contatos da database."""
        colunas = self.tabelas_colunas[tabela][:]
        id_contatos = Utils()._pega_todos_id(api, '/contatos?criterio=1')

        ROTA = '/contatos/'
        log.info(f"Passará por {len(id_contatos)} contatos")
        repeticoes = 1
        for idContato in tqdm(id_contatos):
            log.info(f"Solicita dados do contato {repeticoes} na API")
            contato = api.solicita_na_api(ROTA+f"{idContato}")['data']
            # Pegando informações sobre o contato
            log.info("Manipula dados dos contatos")
            contato_info = ut_contatos()._manipula_dados_contatos(
                contato, fuso, conn, self.tabelas_colunas)

            # Pegando informações referente ao endereço
            contato_endereco = {
                'id_contato': contato['id'],
                'endereco': contato['endereco'],
                'pais': contato['pais'],
                'tipo': contato['tipo']
            }

            log.info("Insere contato")
            self.insert_one_in_db(
                tabela='contatos', colunas=colunas, valores=contato_info,
                valores_placeholder=colunas, conn=conn)
            self.preencher_endereco(conn=conn, dict_endereco=contato_endereco)
            repeticoes += 1

        log.info("Fim")

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
        colunas = self.tabelas_colunas['enderecos'][:]
        colunas.remove('id')

        pais = ut_contatos()._regra_pais(tipo_contato=dict_endereco['tipo'],
                                         pais=dict_endereco['pais']['nome'])

        for tipo_endereco in dict_endereco['endereco'].keys():
            endereco = dict_endereco['endereco'][tipo_endereco]
            if tipo_endereco == 'geral':
                id_tipo_endereco = 0
            elif tipo_endereco == 'cobranca':
                id_tipo_endereco = 1

            if ut_contatos()._possui_informacao(endereco):
                id_pais = ut_contatos()._preencher_campos_endereco(
                    tabela='endereco_paises', campo='nome', campo_nome=pais,
                    conn=conn, tabelas_colunas=self.tabelas_colunas)

                endereco = ut_contatos()._manipula_dados_endereco(
                    endereco, id_pais, conn, self.tabelas_colunas)

                # Inserir na tabela enderecos
                endereco_inserido = self.insert_one_in_db(
                    tabela='enderecos', colunas=colunas, valores=endereco,
                    valores_placeholder=colunas, conn=conn)
                id_endereco = endereco_inserido['id']

                colunas_enderecos_inserido = (
                    self.tabelas_colunas['contatos_enderecos'][:])
                colunas_enderecos_inserido.remove('id')
                valores = {
                    'id_contato': dict_endereco['id_contato'],
                    'id_endereco': id_endereco,
                    'tipo_endereco': id_tipo_endereco
                }
                # Inserir na tabela contatos_enderecos
                self.insert_one_in_db(
                    tabela='contatos_enderecos', valores=valores,
                    colunas=colunas_enderecos_inserido, conn=conn,
                    valores_placeholder=colunas_enderecos_inserido)

        log.info("Fim")

    def preencher_modulo_contatos(self, conn, api, fuso):
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
        log.info("Inicio")
        # with conn.transaction():
        log.info("Inicio preencher contatos_situacao")
        self.preencher_contatos_situacao(tabela='contatos_situacao',
                                         conn=conn)

        log.info("Inicio preencher contatos_tipo")
        self.preencher_contatos_tipo(tabela='contatos_tipo',
                                     conn=conn)

        log.info("Inicio preencher contatos_indicador_inscricao")
        self.preencher_contatos_indicador_inscricao_estadual(
            tabela='contatos_indicador_inscricao_estadual', conn=conn)

        log.info("Inicio preencher contatos_classificacao")
        self.preencher_contatos_classificacao(
            tabela='contatos_classificacao', conn=conn, api=api)

        log.info("Inicio preencher contatos")
        self.preencher_contatos(tabela='contatos', conn=conn,
                                api=api, fuso=fuso)

        log.info("Fim")


if __name__ == "__main__":
    pass
