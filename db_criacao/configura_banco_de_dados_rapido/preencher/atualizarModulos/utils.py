#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 21:04:27 2024.

@author: vcsil
"""
from preencherModulos.utils import (db_pega_um_elemento, db_inserir_uma_linha,
                                    db_pega_varios_elementos)

from config.constants import API, DB, FUSO, TABELAS_COLUNAS
from colorama import Back, Style, Fore
from datetime import datetime
from tqdm import tqdm
import logging

log = logging.getLogger("root")


def api_pega_todos_id_verifica_db(param, tabela_busca, coluna_busca, conn):
    """
    Pega todos o ID de de um determinado canal da API.

    Compara com as linha do banco de dados para realizar a parada.

    Returns
    -------
    List[int]
        Lista com o ids de cada contato.

    """
    list_ids = []  # Vai armazenar as ids
    pagina = 0

    log.info(f"Pega os id's dos dados em {param} até encontrar um no banco")
    barra_carregamento = tqdm(desc=f"Paginas de dados {param}")
    while True:
        pagina += 1
        param_completo = param + f"pagina={pagina}&limite=100"

        # Retorna um list com os dados dentro de dict
        dados_reduzido = API.solicita_na_api(param_completo)["data"]
        if not dados_reduzido:
            break

        list_ids.extend(map(lambda dado: dado["id"], dados_reduzido))

        valor_busca = list_ids[-1]
        existe = db_verifica_se_existe(tabela_busca, coluna_busca,
                                       [valor_busca], conn)
        if existe:
            break

        barra_carregamento.update(1)

    log.info("Fim")
    return list_ids  # Lista invertida = Ordem crescente de data


def db_atualizar_uma_linha(tabela, colunas, valores, coluna_filtro,
                           valor_filtro, conn):
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

    return DB.update_one_in_db(tabela, colunas, valores, coluna_filtro,
                               valor_filtro, conn)


def db_verifica_se_existe(tabela_busca, coluna_busca, valor_busca, conn):
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
    conn: connection
        Connection DB

    Returns
    -------
    dict
        com as colunas de retorno passadas

    """
    colunas_retorno = (coluna_busca if isinstance(coluna_busca, list)
                       else [coluna_busca])
    valor_busca = (valor_busca if isinstance(valor_busca, list)
                   else [valor_busca])

    linha = db_pega_um_elemento(tabela_busca, coluna_busca, valor_busca,
                                colunas_retorno, conn)

    return linha


def solicita_novos_ids(param, tabela_busca, coluna, conn):
    """Solicita ID a API, compara com os ids do banco de dados. Devolve new."""
    ids_api = api_pega_todos_id_verifica_db(param, tabela_busca, coluna, conn)

    ids_db = db_pega_varios_elementos(tabela_busca, coluna, conn)
    ids_db = [item[coluna] for item in ids_db]

    ids = list(set(ids_api) - set(ids_db))
    ids.sort()

    return ids


def solicita_item_novos(param, tabela, colunas_retorno, conn):
    """Solicita items novos fazendo comparação com o ID e retornando objeto."""
    lista_objetos_api = API.solicita_na_api(param)["data"]
    ids_api = [item["id"] for item in lista_objetos_api]

    ids_db = db_pega_varios_elementos(tabela, colunas_retorno, conn)
    ids_db = [item[colunas_retorno] for item in ids_db]

    ids_novos = list(set(ids_api) - set(ids_db))
    ids_novos.sort()

    lista_objetos = []
    for id_procurado in ids_novos:
        dict_encontrado = next(
            (obj for obj in lista_objetos_api if obj["id"] == id_procurado),
            None)
        if dict_encontrado:
            lista_objetos.append(dict_encontrado)

    return lista_objetos


def item_com_valores_atualizados(item_api, tabela, coluna_busca, conn):
    """Busca valores modificados nos elementos. Retorna False se iguais."""
    if (isinstance(coluna_busca, list)):
        valor_busca = [item_api[coluna] for coluna in coluna_busca]
    elif (isinstance(coluna_busca, str)):
        valor_busca = [item_api[coluna_busca]]
    else:
        raise ValueError

    item_db = db_pega_um_elemento(tabela, coluna_busca, valor_busca,
                                  list(item_api.keys()), conn)

    if item_db == item_api:
        return False

    # Caso ele não exista no banco de dados ainda
    if not item_db:
        item_api["alterado_em"] = datetime.now(FUSO)
        db_inserir_uma_linha(tabela, colunas=TABELAS_COLUNAS[tabela],
                             valores=item_api, conn=conn)
        return False

    diff = [k for k in item_api.keys() if item_api[k] != item_db[k]]
    log.info(f"Atualiza colunas: {diff}")
    item_api["alterado_em"] = datetime.now(FUSO)
    return item_api


def txt_fundo_verde(text):
    """Imprime uma mensagem com fundo verde no console."""
    print(Back.GREEN + text + Style.RESET_ALL)
    log.info(text)
    return


def txt_fundo_azul(text):
    """Imprime uma mensagem com fundo azul no console."""
    print(Back.BLUE + text + Style.RESET_ALL)
    log.info(text)
    return


def txt_amarelo(text):
    """Imprime uma mensagem com texto amarelo no console."""
    print(Fore.YELLOW + text + Style.RESET_ALL)
    log.info(text)
    return


def txt_fundo_amarelo(text):
    """Imprime uma mensagem com fundo amarelo no console."""
    print(Back.YELLOW + text + Style.RESET_ALL)
    log.info(text)
    return


def slice_array(array, batch_size):
    """
    Fatiar um array em pedaços de tamanho fixo.

    Args:
      array: O array a ser fatiado.
      batch_size: O tamanho de cada pedaço.

    Returns
    -------
      Uma lista de pedaços do array original.
    """
    return [array[i:i + batch_size] for i in range(0, len(array), batch_size)]


if __name__ == "__main__":
    pass
