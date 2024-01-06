#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 12:43:57 2023.

@author: vcsil
"""
from config.erros.erros import EsqueceuPassarID
from config.conexao_db import ConectaDB

from typing import List, Dict, Union
from datetime import datetime
from tqdm import tqdm
import logging

log = logging.getLogger(__name__)
"""Funções utéis para preencher os módulos."""


def db_inserir_varias_linhas(
    tabela: str,
    colunas: Union[str, List[str]],
    valores: List[Dict[str, Union[str, int]]],
    conn
):
    """
    Insere várias linhas de uma vez na tabela do banco de dados.

    Parameters
    ----------
    tabela : str
        Nome da tabela que vai receber os valores.
    colunas : Union[str, List[str]]
        Nome das colunas que vão receber os valores.
    valores : List[Dict[str, Union[str, int]]]
        Valores que serão inseridos, devem estar dentro de uma list de dict
        Exemplo: [{'id': 0, 'nome': 'a'}]
    conn : Connection
        Conexão com banco de dados.

    Returns
    -------
    None.

    """
    ConectaDB().insert_many_in_db(
        tabela=tabela, colunas=colunas, valores=valores, conn=conn)


def db_inserir_uma_linha(
    tabela: str,
    colunas: Union[str, List[str]],
    valores: List[Dict[str, Union[str, int]]],
    conn
):
    """
    Insere uma linha na tabela do banco de dados.

    Parameters
    ----------
    tabela : str
        Nome da tabela que vai receber os valores.
    colunas : Union[str, List[str]]
        Nome das colunas que vão receber os valores.
    valores : List[Dict[str, Union[str, int]]]
        Valores que serão inseridos, devem estar dentro de uma list de dict
        Exemplo: [{'id': 0, 'nome': 'a'}]
    conn : Connection
        Conexão com banco de dados.

    Returns
    -------
    None.

    """
    return ConectaDB().insert_one_in_db(
        tabela=tabela, colunas=colunas, valores=valores, conn=conn)


def db_pega_um_elemento(
        tabela_busca: str,
        coluna_busca: Union[str, List[str]],
        valor_busca: Union[str, list],
        colunas_retorno: list,
        conn
) -> dict:
    """
    Utilizado para buscar um elemento que já existe.

    Parameters
    ----------
    tabela_busca : str
        Em qual tabela do banco de dados deve ser feita a busca.
        Exemplo: "contatos_tipo"
    coluna_busca : Union[str, List[str]]
        Em qual coluna da tabela deve-se procurar o valor declarado.
        Se a busca considerar mais de uma coluna, deve ser uma list.
        Exemplo: "sigla" ou ["largura", "altura"]
    valor_busca : Union[str, list]
        O elemento que será utilizado como referência para a busca.
        Se a busca considerar mais de um valor, deve ser uma list.
        Exemplo: "F" ou [10, 9]
    colunas_retorno : str
        As respectivas colunas do objeto que será retornado.
        Exemplo: ["id", "nome", "sigla"].
    conn: connection
        Connection DB

    Returns
    -------
    dict
        com as colunas de retorno passadas

    """
    coluna_busca = [coluna_busca] if isinstance(coluna_busca, str) else (
        coluna_busca)
    valor_busca = [valor_busca] if isinstance(valor_busca, str) else (
        valor_busca)

    filtro = "WHERE "
    filtro += " AND ".join(f"{col}='{val}'" for col, val in zip(
        coluna_busca, valor_busca))

    try:
        elemento_dict = ConectaDB().select_one_from_db(
            tabela=tabela_busca, colunas=colunas_retorno, conn=conn,
            filtro=(filtro, ))

        return elemento_dict
    # Erro vai ser chamado ao tentar buscar uma elemento que não existe
    except AttributeError as e:
        print(f"O elemento '{valor_busca}' não existe ", end="")
        print(f"na tabela '{tabela_busca}'")
        print(f"nem na coluna '{tabela_busca}.{coluna_busca}'. : {e}'")


def pega_todos_id(api, param: str) -> List[int]:
    """
    Pega todos o ID de de um determinado canal da API.

    Returns
    -------
    List[int]
        Lista com o ids de cada contato.

    """
    list_ids = []  # Vai armazenar as ids
    tem_dados = True  # Verifica se tem dados na página
    pagina = 0

    log.info(f"Pega os id's de todos os dados em {param}")
    barra_carregamento = tqdm(desc=f'Paginas de dados {param}')
    while tem_dados:
        pagina += 1
        param_completo = param + f'pagina={pagina}&limite=100'

        dados_reduzido = api.solicita_na_api(param_completo)['data']
        # Retorna um list com os dados dentro de dict

        if (len(dados_reduzido)) > 0:
            for dados in dados_reduzido:
                list_ids.append(dados['id'])

            barra_carregamento.update(1)
        else:
            tem_dados = False
        # tem_dados = False  # <<<<<<<<<<<<<<<<<

    log.info("Fim")
    return list_ids[::-1]  # Lista invertida = Ordem crescente de data


def _pega_valor_id_do_dict(elemento):
    """Recebe elemento direto do banco de dados e busca o id referente."""
    for key in elemento.keys():
        if (key == "id") or (key == "id_bling"):
            return elemento[key]
    else:
        raise EsqueceuPassarID()


def verifica_preenche_valor(
        tabela_busca: str,
        coluna_busca: Union[str, List[str]],
        valor_busca: Union[str, List[str]],
        list_colunas,
        conn,
        relacao_externa: Dict[str, int] = None
) -> int:
    """
    Confere se o dado existe, se não existir insere e retorna o ID.

    Verifica se dado já existe no banco de dados e retorna id
    Ex.: Verifica se o estado "GO" já existe e retorna id, caso
    contrário, adiciona o novo estado no banco de dados.

    Parameters
    ----------
    tabela_busca : str
        Tabela para buscar/inserir o dado.
    coluna_busca : Union[str, List[str]]
        Nome da coluna da tabela a ser feita a busca.
        Se a busca for em mais de uma coluna, deve ser uma list com nomes.
    valor_busca : Union[str, List[str]]
        Valor a ser procurado/inserido.
        Se a busca for em mais de uma coluna, deve ser em list com valores.
    list_colunas :
        Lsita com o nome de todas as colunas da tabela.
    conn : str
        connection banco de dados
    relacao_externa : Dict[str, int]
        Dict com nome da coluna de relação e o respectivo id.

    Returns
    -------
    id do campo: int

    """
    # Procura ID do campo
    try:
        campo_ja_existe = db_pega_um_elemento(
            tabela_busca=tabela_busca, coluna_busca=coluna_busca,
            valor_busca=valor_busca, colunas_retorno=list_colunas, conn=conn)

        id_campo = _pega_valor_id_do_dict(campo_ja_existe)

        return id_campo
    except AttributeError:
        if isinstance(coluna_busca, str):
            coluna_busca = [coluna_busca]
            valor_busca = [valor_busca]
        valores = {key: valores for key, valores in zip(coluna_busca,
                                                        valor_busca)}

        # Adicona relações
        if relacao_externa:
            valores = {**valores, **{chave: valor
                                     for chave, valor
                                     in relacao_externa.items()}}

        dados_inseridos = db_inserir_uma_linha(
            tabela=tabela_busca, colunas=valores.keys(), valores=valores,
            conn=conn)

        id_campo = _pega_valor_id_do_dict(dados_inseridos)
        return id_campo


def formata_data(data: str):
    """Formata data para o padrão do banco de dados."""
    ano, mes, dia = data.split('-')
    if ano == "0000":
        return None
    else:
        return datetime(int(ano), int(mes), int(dia))


if __name__ == "__main__":
    pass
