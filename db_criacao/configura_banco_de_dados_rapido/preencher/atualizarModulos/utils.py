#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 21:04:27 2024.

@author: vcsil
"""
from preencherModulos.utils import (db_pega_um_elemento, api_pega_todos_id,
                                    db_pega_varios_elementos)

from tqdm import tqdm
import logging

log = logging.getLogger(__name__)


def api_pega_todos_id_verifica_db(api, db, param, tabela_busca,
                                  coluna_busca, colunas_retorno,
                                  conn):
    """
    Pega todos o ID de de um determinado canal da API.

    Compara com as linha do banco de dados para realizar a parada.

    Returns
    -------
    List[int]
        Lista com o ids de cada contato.

    """
    list_ids = []  # Vai armazenar as ids
    tem_dados = True  # Verifica se tem dados na página
    pagina = 0

    log.info(f"Pega os id's dos dados em {param} até encontrar um no banco")
    barra_carregamento = tqdm(desc=f'Paginas de dados {param}')
    while tem_dados:
        pagina += 1
        param_completo = param + f'pagina={pagina}&limite=100'

        dados_reduzido = api.solicita_na_api(param_completo)['data']
        # Retorna um list com os dados dentro de dict

        if (len(dados_reduzido)) > 0:
            for dados in dados_reduzido:
                list_ids.append(dados['id'])

            valor_busca = list_ids[-1]
            existe = db_pega_um_elemento(
                tabela_busca=tabela_busca, coluna_busca=coluna_busca,
                valor_busca=[valor_busca], colunas_retorno=colunas_retorno,
                db=db, conn=conn)

            if existe:
                tem_dados = False
            barra_carregamento.update(1)
        else:
            tem_dados = False

    log.info("Fim")
    return list_ids  # Lista invertida = Ordem crescente de data


def db_atualizar_uma_linha(
    tabela,
    colunas,
    valores,
    coluna_filtro,
    valor_filtro,
    db,
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
    coluna_filtro = (coluna_filtro if isinstance(coluna_filtro, list)
                     else [coluna_filtro])
    valor_filtro = (valor_filtro if isinstance(valor_filtro, list)
                    else [valor_filtro])

    return db.update_one_in_db(
        tabela=tabela, colunas=colunas, valores=valores, conn=conn,
        coluna_filtro=coluna_filtro, valor_filtro=valor_filtro)


def db_verifica_se_existe(tabela_busca, coluna_busca, valor_busca,
                          colunas_retorno, conn, db):
    """
    Utilizado para verificar se um elemento já existe a partir do seu ID.

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
    coluna_busca = (colunas_retorno if isinstance(colunas_retorno, list)
                    else [colunas_retorno])
    valor_busca = (valor_busca if isinstance(valor_busca, list)
                   else [valor_busca])

    linha = db_pega_um_elemento(
        tabela_busca=tabela_busca, coluna_busca=coluna_busca, conn=conn,
        valor_busca=valor_busca, colunas_retorno=colunas_retorno, db=db)

    return bool(linha)


def solicita_novos_ids(param, tabela_busca, coluna_busca, coluna_retorno,
                       conn, api, db):
    """Solicita ID a API, compara com os ids do banco de dados. Devolve new."""
    ids_api = api_pega_todos_id_verifica_db(
        api=api, db=db, param=param, tabela_busca=tabela_busca,
        coluna_busca=coluna_busca, colunas_retorno=coluna_retorno, conn=conn)

    ids_db = db_pega_varios_elementos(tabela_busca=tabela_busca, conn=conn,
                                      colunas_retorno=coluna_retorno, db=db)
    ids_db = [item[coluna_retorno] for item in ids_db]

    ids = list(set(ids_api) - set(ids_db))
    ids.sort()

    return ids
