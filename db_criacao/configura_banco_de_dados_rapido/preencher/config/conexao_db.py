#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 11:13:16 2023.

@author: vcsil
"""
from typing import List, Tuple, Dict, Union
from psycopg import sql, connect, Error
from psycopg.rows import dict_row
from tqdm import tqdm
import logging
import sys

log = logging.getLogger('root')

# =-=-=-=-=-=-=-=-=-=-=-=-= Conexão ao Banco de Dados =-=-=-=-=-=-=-=-=-=-=-=-=


class ConectaDB():
    """Controla conexão com o banco de dados."""

    def __init__(self, env_db):
        self._env = env_db

    def conectar_ao_banco(self):
        """
        Conecta ao banco de dados.

        Returns
        -------
        psycopg.connect
            conexão com banco de dados.

        """
        conn_string = f"""
            dbname={self._env["POSTGRES_DB"]}
            user={self._env["POSTGRES_USER"]}
            password={self._env["POSTGRES_PASSWORD"]}
            host={self._env["POSTGRES_HOST"]}
            port={self._env["POSTGRES_HOST_PORT"]}
        """
        try:
            log.info('Inicia conexão com banco de dados')
            conn = connect(conn_string, row_factory=dict_row)
            return conn
        except Error as e:
            _, _, traceback_obj = sys.exc_info()
            print(f"SQLState: {e.sqlstate}")
            print(f"Erro no banco de dados: {e}\n{type(e)}")
            print(f"{traceback_obj}\n")
            log.error(f"SQLState: {e.sqlstate} {e}")
            conn.rollback()

    def select_all_from_db(
            self,
            tabela: str,
            colunas: Union[str, List[str]],
            conn,
            filtro: Tuple[str, Tuple[Union[str, int]]] = None
    ) -> List[Tuple[int]]:
        """
        Faz um SELECT no banco de dados.

        É possivel definir a tabela, as colunas e algum tipo de filtro

        Parameters
        ----------
        tabela : str
            Nome da tabela.
        colunas : Union[str, List[str]]
            Nome da coluna ou um array com o nome das colunas .
        conn : Connection
            Conexão com banco de dados.
        filtro : Tuple[str, Tuple[Union[str, int]]], optional
            Uma tupla com o Filtro seguindo por uma tupla com o valor do
            filtro. The default is None.

        Returns
        -------
        List[Tuple[int]]
            Uma lista com as linhas em forma de tupla com os dados.

        """
        query = self._constroi_query_busca(tabela, colunas, filtro)

        try:
            log.info(f"Solicita varios: {query.as_string(conn)}")
            # with conn.transaction():
            # print(query.as_string(conn))
            array_dados = conn.execute(query).fetchall()

            log.info("Sucesso na solicitação")
            return array_dados
        except Error as e:
            _, _, traceback_obj = sys.exc_info()
            print(f"SQLState: {e.sqlstate}")
            print(f"Erro no banco de dados: {e}\n{type(e)}")
            print(f"{traceback_obj}\n")
            log.error(f"{query.as_string(conn)}")
            log.error(f"SQLState: {e.sqlstate} {e}")
            conn.rollback()
            sys.exit()

    def select_all_from_db_like_as(
            self,
            tabela: str,
            colunas: Union[str, List[str]],
            conn,
            filtro: str
    ) -> List[Tuple[int]]:
        """
        Faz um SELECT no banco de dados podendo digitar o filtro.

        É possivel definir a tabela, as colunas

        Parameters
        ----------
        tabela : str
            Nome da tabela.
        colunas : Union[str, List[str]]
            Nome da coluna ou um array com o nome das colunas .
        conn : Connection
            Conexão com banco de dados.
        filtro : Tuple[str, Tuple[Union[str, int]]], optional
            Uma tupla com o Filtro seguindo por uma tupla com o valor do
            filtro. The default is None.

        Returns
        -------
        List[Tuple[int]]
            Uma lista com as linhas em forma de tupla com os dados.

        """
        query = (
            sql.SQL("SELECT {columns} FROM {table} {fltr}")
            .format(
                columns=sql.SQL(',').join(
                    map(sql.Identifier, colunas)
                ),
                table=sql.SQL(tabela),
                fltr=sql.SQL(filtro)
            )
        )

        try:
            log.info(f"Solicita varios: {query.as_string(conn)}")
            # with conn.transaction():
            # print(query.as_string(conn))
            array_dados = conn.execute(query).fetchall()

            log.info("Sucesso na solicitação")
            return array_dados
        except Error as e:
            _, _, traceback_obj = sys.exc_info()
            print(f"SQLState: {e.sqlstate}")
            print(f"Erro no banco de dados: {e}\n{type(e)}")
            print(f"{traceback_obj}\n")
            log.error(f"{query.as_string(conn)}")
            log.error(f"SQLState: {e.sqlstate} {e}")
            conn.rollback()
            sys.exit()

    def select_one_from_db(
            self,
            tabela: str,
            colunas: Union[str, List[str]],
            conn,
            filtro: Tuple[str, Tuple[Union[str, int]]] = None
    ) -> List[Tuple[int]]:
        """
        Faz um SELECT no banco de dados.

        É possivel definir a tabela, as colunas e algum tipo de filtro

        Parameters
        ----------
        tabela : str
            Nome da tabela.
        colunas : Union[str, List[str]]
            Nome da coluna ou um array com o nome das colunas que serão
            retornadas.
        conn : Connection
            Conexão com banco de dados.
        filtro : Tuple[str, Tuple[Union[str, int]]], optional
            Uma tupla com o Filtro seguindo por uma tupla com o valor do
            filtro. The default is None.

        Returns
        -------
        List[Tuple[int]]
            Uma lista com as linhas em forma de tupla com os dados.

        """
        query = self._constroi_query_busca(tabela, colunas, filtro)

        try:
            log.info(f"Solicita um: {query.as_string(conn)}")
            # with conn.transaction():
            # print(query.as_string(conn))
            array_dados = conn.execute(query).fetchone()

            log.info("Sucesso na solicitação")
            return array_dados
        except Error as e:
            _, _, traceback_obj = sys.exc_info()
            print(f"SQLState: {e.sqlstate}")
            print(f"Erro no banco de dados: {e}\n{type(e)}")
            print(f"{traceback_obj}\n")
            log.error(f"{query.as_string(conn)}")
            log.error(f"SQLState: {e.sqlstate} {e}")
            conn.rollback()
            sys.exit()

    def _constroi_query_busca(
            self,
            tabela: str,
            colunas: Union[str, List[str]],
            filtro: Tuple[str, Tuple[Union[str, int]]] = None
    ):
        if isinstance(colunas, str):
            colunas = [colunas]

        query = (
            sql.SQL("SELECT {columns} FROM {table}")
            .format(
                columns=sql.SQL(',').join(
                    map(sql.Identifier, colunas)
                ),
                table=sql.SQL(tabela)
            )
        )
        if filtro:
            query = sql.SQL("{query_fixa} WHERE {fltr}").format(
                query_fixa=query,
                fltr=sql.SQL(" AND ").join(
                    sql.SQL("{coluna}={valor}").format(
                        coluna=sql.Identifier(col),
                        valor=sql.Literal(val)
                    ) for col, val in zip(filtro[0], filtro[1])
                )
            )
        return query

    def insert_many_in_db(
            self,
            tabela: str,
            colunas: Union[str, List[str]],
            valores: List[Dict[str, Union[str, int]]],
            conn
    ):
        """
        Faz um INSERT de várias linhas de dados no banco de dados.

        Parameters
        ----------
        tabela : str
            Nome da tabela que recebera o valor.
        colunas : Union[str, List[str]]
            Nome das colunas que receberam os valores.
        valores : List[Dict[str, Union[str, int]]]
            Um dict com os valores a serem inseridos, as chaves são as colunas.
        conn : Connection
            Conexão com banco de dados.

        Returns
        -------
        None.

        """
        if not isinstance(valores, list):
            valores = [valores]

        query = (
            sql.SQL("INSERT INTO {table} ({columns}) VALUES ({values})")
            .format(
                table=sql.Identifier(tabela),
                columns=sql.SQL(',').join(
                        map(sql.Identifier, colunas)
                ),
                values=sql.SQL(', ').join(
                        map(sql.Placeholder, colunas)
                )
            )
        )
        try:
            log.info(f"Insere varios na tabela {tabela}")
            # with conn.transaction():
            # print(query.as_string(conn))
            with conn.cursor() as cur:
                cur.executemany(query, valores)
            log.info("Sucesso na inserção")
        except Error as e:
            _, _, traceback_obj = sys.exc_info()
            print(f"SQLState: {e.sqlstate}")
            print(f"Erro no banco de dados: {e}\n{type(e)}")
            print(f"{traceback_obj}\n")
            log.error(f"SQLState: {e.sqlstate} {e}")
            log.error(f"{query.as_string(conn)} [{valores}]")
            conn.rollback()
            sys.exit()

    def insert_one_in_db(
            self,
            tabela: str,
            colunas: Union[str, List[str]],
            valores: Dict[str, Union[str, int]],
            conn
    ):
        """
        Faz um INSERT de uma linha de dados no banco de dados.

        Parameters
        ----------
        tabela : str
            Nome da tabela que recebera o valor.
        colunas : Union[str, List[str]]
            Nome das colunas que receberam os valores.
        valores : Dict[str, Union[str, int]]
            Um dict com os valores a serem inseridos, as chaves são as colunas.
        conn : Connection
            Conexão com banco de dados.

        Returns
        -------
        None.

        """
        query = "INSERT INTO {table} ({columns}) VALUES ({values}) RETURNING *"
        query = (sql.SQL(query).format(
            table=sql.Identifier(tabela),
            columns=sql.SQL(',').join(
                map(sql.Identifier, colunas)
                ),
            values=sql.SQL(', ').join(
                map(sql.Placeholder, colunas)
                )
            )
        )
        try:
            log.info(f"Insere um na tabela {tabela}")
            # with conn.transaction():
            # print(query.as_string(conn))
            dados_inseridos = conn.execute(query, valores).fetchone()
            log.info("Sucesso na inserção")
            return dados_inseridos
        except Error as e:
            _, _, traceback_obj = sys.exc_info()
            print(f"SQLState: {e.sqlstate}")
            print(f"Erro no banco de dados: {e}\n{type(e)}")
            print(f"{traceback_obj}\n")
            log.error(f"SQLState: {e.sqlstate} {e}")
            log.error(f"{query.as_string(conn)} [{valores}]")
            conn.rollback()
            sys.exit()

    def update_one_in_db(
            self,
            tabela: str,
            colunas: Union[str, List[str]],
            valores: Dict[str, Union[str, int]],
            coluna_filtro,
            valor_filtro,
            conn
    ):
        """
        Faz um UPDATE de uma linha de dados no banco de dados.

        Parameters
        ----------
        tabela : str
            Nome da tabela que recebera o valor.
        colunas : Union[str, List[str]]
            Nome das colunas que receberam os valores.
        valores : Dict[str, Union[str, int]]
            Um dict com os valores a serem inseridos, as chaves são as colunas.
        coluna_filtro:
            Coluna para buscar valor.
        valor_filtro:
            Valor identificar linha que vai ser alterada.
        conn : Connection
            Conexão com banco de dados.

        Returns
        -------
        None.

        """
        query = "UPDATE {table} SET ({columns}) = ({values}) "
        query += "WHERE {filtr} RETURNING *"
        query = (sql.SQL(query).format(
            table=sql.Identifier(tabela),
            columns=sql.SQL(',').join(
                map(sql.Identifier, colunas)
                ),
            values=sql.SQL(', ').join(
                map(sql.Placeholder, colunas)
                ),
            filtr=sql.SQL(" AND ").join(
                sql.SQL("{coluna}={valor}").format(
                    coluna=sql.Identifier(col),
                    valor=sql.Literal(val)
                ) for col, val in zip(coluna_filtro, valor_filtro)
            )
            )
        )
        try:
            log.info(f"Atualiza um na tabela {tabela}")
            # with conn.transaction():
            # print(query.as_string(conn))
            dados_inseridos = conn.execute(query, valores).fetchone()
            log.info("Sucesso na atualização")
            return dados_inseridos
        except Error as e:
            _, _, traceback_obj = sys.exc_info()
            print(f"SQLState: {e.sqlstate}")
            print(f"Erro no banco de dados: {e}\n{type(e)}")
            print(f"{traceback_obj}\n")
            log.error(f"SQLState: {e.sqlstate} {e}")
            log.error(f"{query.as_string(conn)} [{valores}]")
            conn.rollback()
            sys.exit()

    def delete_one_in_db(
            self,
            tabela: str,
            coluna_filtro,
            valor_filtro,
            conn
    ):
        """
        Faz um DELETE de uma linha de dados no banco de dados.

        Parameters
        ----------
        tabela : str
            Nome da tabela que sofrera a alteracao.
        coluna_filtro:
            Coluna para buscar valor.
        valor_filtro:
            Valor para identificar linha que vai ser excluida.
        conn : Connection
            Conexão com banco de dados.

        Returns
        -------
        None.

        """
        query = "DELETE FROM {table} "
        query += "WHERE {column} = {value} RETURNING *"
        query = (sql.SQL(query).format(
            table=sql.Identifier(tabela),
            column=sql.Identifier(coluna_filtro),
            value=sql.Literal(valor_filtro),
            )
        )
        try:
            txt = f"Deleta uma linha na tabela '{tabela}' com o valor "
            txt += f"'{valor_filtro}' na coluna '{coluna_filtro}'"
            log.info(txt)
            # with conn.transaction():
            # print(query.as_string(conn))
            dados_excluidos = conn.execute(query).fetchone()
            log.info("Sucesso na exclusão")
            return dados_excluidos
        except Error as e:
            _, _, traceback_obj = sys.exc_info()
            print(f"SQLState: {e.sqlstate}")
            print(f"Erro no banco de dados: {e}\n{type(e)}")
            print(f"{traceback_obj}\n")
            log.error(f"SQLState: {e.sqlstate} {e}")
            log.error(f"{query.as_string(conn)}")
            conn.rollback()
            sys.exit()

    def delete_many_in_db(
            self,
            tabela: str,
            coluna_filtro,
            valores_filtro,
            conn
    ):
        """
        Faz um DELETE de varias linhas de dados no banco de dados.

        Parameters
        ----------
        tabela : str
            Nome da tabela que sofrera a alteracao.
        coluna_filtro:
            Coluna para buscar valor.
        valores_filtro:
            Valores para identificar linhas que serão excluidas.
        conn : Connection
            Conexão com banco de dados.

        Returns
        -------
        None.

        """
        query = "DELETE FROM {table} "
        query += "WHERE ({column}) IN ({values}) RETURNING *"
        query = (sql.SQL(query).format(
            table=sql.Identifier(tabela),
            column=sql.Identifier(coluna_filtro),
            values=sql.SQL(', ').join(map(sql.Literal, valores_filtro))
            )
        )
        try:
            txt = f"Deleta linhas na tabela '{tabela}' com os valores "
            txt += f"'{valores_filtro}' na coluna '{coluna_filtro}'"
            log.info(txt)
            # with conn.transaction():
            # print(query.as_string(conn))
            dados_excluidos = conn.execute(query).fetchone()
            log.info("Sucesso na exclusão")
            return dados_excluidos
        except Error as e:
            _, _, traceback_obj = sys.exc_info()
            print(f"SQLState: {e.sqlstate}")
            print(f"Erro no banco de dados: {e}\n{type(e)}")
            print(f"{traceback_obj}\n")
            log.error(f"SQLState: {e.sqlstate} {e}")
            log.error(f"{query.as_string(conn)}")
            conn.rollback()
            sys.exit()

    def pega_nome_tabelas(self) -> List[str]:
        """
        Pega nome da todas as tabelas do banco de dados.

        Returns
        -------
        List[str]
            Lista com o nome das tabelas.

        """
        with self.conectar_ao_banco() as conn:
            nome_tabelas = self.select_all_from_db(
                tabela=('"information_schema"."tables"'), conn=conn,
                colunas="table_name", filtro=(["table_schema"], ['public']))
        # Tirar valores de dentro do dict e colocar na list
        nome_tabelas = [tabela['table_name'] for tabela in nome_tabelas]
        return nome_tabelas

    def pega_nome_colunas(self, tabela: str) -> List[str]:
        """
        Pegar o nome de todas as colunas de uma tabela.

        Parameters
        ----------
        tabela : str
            Nome da tabela.

        Returns
        -------
        array_dados : List[str]
            Lista de tupla com os nomes das colunas.

        """
        with self.conectar_ao_banco() as conn:
            nome_colunas = self.select_all_from_db(
                tabela='"information_schema"."columns"',
                colunas="column_name", filtro=(["table_name"], [tabela]),
                conn=conn)

        # Tirar os valores do dict e deixar dentro de uma array
        nome_colunas = [coluna['column_name'] for coluna in nome_colunas]

        return nome_colunas

    def cria_dict_tabelas_colunas(self):
        """Usada para gerar um dict com o nome das colunas de cada tabela."""
        tabelas_colunas = {}
        log.info("Pega nome de todas as tabelas")
        db_tabelas = self.pega_nome_tabelas()

        texto_barra_carregar = "Pegando nome das colunas das tabelas"
        for tabela in tqdm(db_tabelas, desc=texto_barra_carregar, position=1):
            log.info(f"Pegando nome das colunas da tabela: {tabela}")
            tabelas_colunas[tabela] = self.pega_nome_colunas(tabela)

        return tabelas_colunas

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


if __name__ == "__main__":
    pass
