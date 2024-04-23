#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 12:43:57 2023.

@author: vcsil
"""
from config.erros.erros import EsqueceuPassarID

from config.constants import API, DB, TABELAS_COLUNAS
from typing import List, Dict, Union
from datetime import datetime
from tqdm import tqdm
import logging

log = logging.getLogger("root")
"""Funções utéis para preencher os módulos."""


def db_inserir_varias_linhas(
    tabela: str,
    colunas: List[str],
    valores: List[Dict[str, Union[str, int]]],
    conn
):
    """
    Insere várias linhas de uma vez na tabela do banco de dados.

    Parameters
    ----------
    tabela : str
        Nome da tabela que vai receber os valores.
    colunas : List[str]
        Lista com nome(s) das colunas que vão receber os valores.
    valores : List[Dict[str, Union[str, int]]]
        Valores que serão inseridos, devem estar dentro de uma list de dict
        Exemplo: [{'id': 0, 'nome': 'a'}]
    conn : Connection
        Conexão com banco de dados.

    Returns
    -------
    None.

    """
    DB.insert_many_in_db(tabela, colunas, valores, conn)


def db_inserir_uma_linha(
    tabela: str,
    colunas: Union[str, List[str]],
    valores: List[Dict[str, Union[str, int]]],
    conn
):
    """
    Insere uma linha na tabela do banco de dados. Aceita dict.

    Parameters
    ----------
    tabela : str
        Nome da tabela que vai receber os valores.
    colunas : List[str]
        Lista de nome(s) das colunas que vão receber os valores.
    valores : List[Dict[str, Union[str, int]]]
        O valor inserido deve ser um dict
        Exemplo: {'id': 0, 'nome': 'a'}
    conn : Connection
        Conexão com banco de dados.

    Returns
    -------
    None.

    """
    return DB.insert_one_in_db(tabela, colunas, valores, conn)


def db_pega_um_elemento(
        tabela_busca: str,
        coluna_busca: Union[str, List[str]],
        valor_busca: Union[str, list],
        colunas_retorno: list,
        conn
) -> Union[dict, None]:
    """
    Utilizado para buscar um elemento que já existe no banco de dados.

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

    try:
        elemento_dict = DB.select_one_from_db(tabela_busca, colunas_retorno,
                                              conn,
                                              (coluna_busca, valor_busca))

        return elemento_dict
    # Erro vai ser chamado ao tentar buscar uma elemento que não existe
    except AttributeError as e:
        log.info(f"O elemento '{valor_busca}' não existe ", end="")
        log.info(f"na tabela '{tabela_busca}'")
        log.info(f"nem na coluna '{tabela_busca}.{coluna_busca}'. : {e}'")


def db_pega_varios_elementos(
        tabela_busca: str,
        colunas_retorno: list,
        conn,
        coluna_busca: Union[str, List[str]] = None,
        valor_busca: Union[str, list] = None,
) -> dict:
    """
    Utilizado para buscar varios elementos que já existem.

    Retorne todos os elementos com ou sem filtro.

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
    colunas_retorno :List[str]
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
    filtro = ((coluna_busca, valor_busca) if coluna_busca and valor_busca
              else None)

    try:
        elemento_dict = DB.select_all_from_db(tabela_busca, colunas_retorno,
                                              conn, filtro)

        return elemento_dict
    # Erro vai ser chamado ao tentar buscar uma elemento que não existe
    except AttributeError as e:
        log.info(f"O elemento '{valor_busca}' não existe ", end="")
        log.info(f"na tabela '{tabela_busca}'")
        log.info(f"nem na coluna '{tabela_busca}.{coluna_busca}'. : {e}'")


def db_pega_varios_elementos_controi_filtro(
        tabela_busca: str,
        filtro: str,
        colunas_retorno: list,
        conn
) -> dict:
    """
    Utilizado para buscar varios elementos que já existem a partir de filtro.

    Parameters
    ----------
    tabela_busca : str
        Em qual tabela do banco de dados deve ser feita a busca.
        Exemplo: "contatos_tipo"
    filtro: str
        O filtro utilizado para busca
        Exemplo: "WHERE id=1 AND historico LIKE 'Ref.%'"
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
    try:
        elemento_dict = DB.select_all_from_db_like_as(tabela_busca,
                                                      colunas_retorno, conn,
                                                      filtro)

        return elemento_dict
    # Erro vai ser chamado ao tentar buscar uma elemento que não existe
    except AttributeError as e:
        log.info(f"O filtro '{filtro}' deu errado", end="")
        log.info(f"na tabela '{tabela_busca}'")
        log.info(e)


def api_pega_todos_id(param: str, pag_unica: bool = False) -> List[int]:
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
    barra_carregamento = tqdm(desc=f"Paginas de dados {param}")
    while tem_dados:
        pagina += 1
        param_completo = param + f"pagina={pagina}&limite=100"

        dados_reduzido = API.solicita_na_api(param_completo)["data"]
        # Retorna um list com os dados dentro de dict

        if (len(dados_reduzido)) > 0:
            for dados in dados_reduzido:
                list_ids.append(dados["id"])

            barra_carregamento.update(1)
            if pag_unica:
                tem_dados = False
        else:
            tem_dados = False

    log.info("Fim")
    return list_ids  # Lista invertida = Ordem crescente de data


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
        campo_ja_existe = db_pega_um_elemento(tabela_busca, coluna_busca,
                                              valor_busca, list_colunas, conn)

        id_campo = _pega_valor_id_do_dict(campo_ja_existe)

        return id_campo
    except AttributeError:
        # Verifica se é só um argumento ou um array de argumentos.
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

        dados_inseridos = db_inserir_uma_linha(tabela_busca, valores.keys(),
                                               valores, conn)

        id_campo = _pega_valor_id_do_dict(dados_inseridos)
        return id_campo


def formata_data(data: str):
    """Formata data para o padrão do banco de dados."""
    ano, mes, dia = data.split("-")
    if ano == "0000":
        return None
    else:
        return datetime(int(ano), int(mes), int(dia))


def possui_informacao(dict_dados: Dict[str, Union[str, int, None]]) -> bool:
    """Verifica se dict contém alguma informação."""
    for valor in dict_dados.values():
        if isinstance(valor, str):
            if len(valor.split()) > 0:
                return True
        else:
            return True
    return False


def manipula_dados_endereco(
        dict_endereco: Dict[str, str],
        id_pais: int,
        conn,
) -> Dict[str, Union[str, int]]:
    """
    Adequa os dados do endereço ao formato do banco de dados.

    Parameters
    ----------
    dict_endereco : Dict[str, str]
        Dicionário de endereço.
    id_pais : int
        Referente ao país de endereço.
        Dicionário de endereço.
    conn :
        Connection.

    Returns
    -------
    Dict[str, Union[str, int]]
        DESCRIPTION.

    """
    log.info("Manipula dados contatos")

    uf = "".join(dict_endereco["uf"].split()).upper()
    list_colunas = TABELAS_COLUNAS["endereco_unidade_federativa"][:]
    id_uf = verifica_preenche_valor("endereco_unidade_federativa", "nome", uf,
                                    list_colunas, conn, {"id_pais": id_pais})

    municipio = " ".join(dict_endereco["municipio"].split()).title()
    list_colunas = TABELAS_COLUNAS["endereco_municipios"][:]
    id_municipio = verifica_preenche_valor("endereco_municipios", "nome",
                                           municipio, list_colunas, conn,
                                           {"id_uf": id_uf})

    bairro = " ".join(dict_endereco["bairro"].split()).title()
    list_colunas = TABELAS_COLUNAS["endereco_bairros"][:]
    id_bairro = verifica_preenche_valor("endereco_bairros", "nome", bairro,
                                        list_colunas, conn,
                                        {"id_municipio": id_municipio})

    numero = dict_endereco["numero"]
    complemento = " ".join(dict_endereco["complemento"].split()).title()
    endereco = {
        "endereco": " ".join(dict_endereco["endereco"].split()).title(),
        "cep": dict_endereco["cep"],
        "id_bairro": id_bairro,
        "id_municipio": id_municipio,
        "id_uf": id_uf,
        "id_pais": id_pais,
        "numero": numero if numero else None,
        "complemento": complemento if complemento else None
    }
    return endereco


def _verifica_contato(id_contato, conn):
    contato_exite = db_pega_um_elemento("contatos", "id_bling", [id_contato],
                                        "id_bling", conn)

    if contato_exite:
        return
    else:
        from preencherModulos.preencherContatos.preencher_contatos import (
            PreencherContatos)
        PreencherContatos().preencher_contatos(conn,
                                               unicoContatoNovo=[id_contato])
        return


if __name__ == "__main__":
    pass
