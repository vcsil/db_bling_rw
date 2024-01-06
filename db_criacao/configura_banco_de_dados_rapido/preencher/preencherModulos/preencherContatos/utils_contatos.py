#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 11:11:39 2023.

@author: vcsil
"""
from preencherModulos.utils import (db_pega_um_elemento, formata_data,
                                    verifica_preenche_valor)

from typing import Dict, Union
from datetime import datetime
import logging

log = logging.getLogger(__name__)

"""Funções utéis para preencher contatos."""


def manipula_dados_contatos(contato: dict, fuso, conn, tabelas_colunas):
    """
    Manipula as informações obtidas pela API e adequa para o banco de dados.

    Parameters
    ----------
    contato : dict
        Resposta da API pura.
    fuso : pytz
        Fuso horário de Brasília.
    conn : connection.bancodedados
        Conexão com banco de dados.
    tabelas_colunas : dict
        Dict com o nome das colunas de cada tabela.

    Returns
    -------
    contato_info : dict
        contato adequado.

    """
    contato_info = {
        'id_bling': contato['id'],
        'nome': (contato['nome'].split()[0]).title(),
        'sobrenome': ' '.join(contato['nome'].split()[1:]).title(),
        'codigo': contato['codigo'],
        'id_situacao_contato': db_pega_um_elemento(
            tabela_busca="contatos_situacao", coluna_busca="sigla",
            valor_busca=contato['situacao'], colunas_retorno=["id"],
            conn=conn)["id"],
        'numero_documento': contato['numeroDocumento'],
        'telefone': _formata_numero_telcel(contato['telefone']),
        'celular': _formata_numero_telcel(contato['celular']),
        'fantasia': contato['fantasia'],
        'id_tipo_contato': db_pega_um_elemento(
            tabela_busca="contatos_tipo", coluna_busca="sigla",
            valor_busca=contato['tipo'], colunas_retorno=["id"],
            conn=conn)["id"],
        'id_indicador_inscricao_estadual': contato['indicadorIe'],
        'inscricao_estadual': contato['ie'],
        'rg': contato['rg'],
        'orgao_emissor': contato['orgaoEmissor'],
        'email': contato['email'],
        'data_nascimento': formata_data(
            contato['dadosAdicionais']['dataNascimento']),
        'sexo': _formata_sexo(contato['dadosAdicionais']['sexo']),
        'id_classificacao_contato': _formata_classificacao(
            contato['tiposContato']),
        'cliente_desde': datetime.now(fuso)
    }
    for chave, valor in contato_info.items():
        if (valor == ''):
            if (chave != "sobrenome"):
                contato_info[chave] = None

    log.info("Fim")
    return contato_info


def _formata_numero_telcel(numero_string: str) -> str:
    if (numero_string == ""):
        return None

    try:
        numero_string = numero_string.replace('+', '')
        numero_string = numero_string.replace('(', '')
        numero_string = numero_string.replace(')', '')
        numero_string = numero_string.replace('-', '')
        numero_string = numero_string.replace(' ', '')
        numero_string = numero_string.replace('xx', '62')
        if (numero_string[0] == '0'):
            numero_string = numero_string[1:]
    except Exception as e:
        print(f"Numero causador: {numero_string}.\n{e}")

    tamanho_numero = len(numero_string)

    if (tamanho_numero == 11):
        numero = '+55' + numero_string
        return numero
    elif (tamanho_numero == 10):
        numero = '+55{}9{}'.format(numero_string[:2], numero_string[2:])
        return numero
    else:
        numero = '+' + numero_string
        return numero


def _formata_sexo(sexo_bling: str):
    sexo_bling = sexo_bling.upper()
    if (sexo_bling == 'F') or (sexo_bling == ''):
        return 2
    elif sexo_bling == 'M':
        return 1
    else:
        return 3


def _formata_classificacao(ja_tem_tipo_contato: list):
    return ja_tem_tipo_contato[0]['id'] if ja_tem_tipo_contato else 14572462908


def regra_pais(tipo_contato: str, pais: str) -> str:
    """
    Define padrão utilizado para adicionar Paises.

    Parameters
    ----------
    tipo_contato : str
        Tipo de contato. Físico, Jurídico, Estrangeira.
    pais : str
        País de endereço.

    Returns
    -------
    str
        Nome do país.

    """
    # Pessoas não estrangeira são assumidas como residente do Brasil
    pessoa_estrangeira = tipo_contato == 'E'
    pais_declarado = len(pais) > 0
    pais = pais if pessoa_estrangeira and pais_declarado else 'Brasil'
    pais = ' '.join(pais.split()).title()

    return pais


def possui_informacao(dict_dados: Dict[str, Union[str, int, None]]) -> bool:
    """Verifica se dict contém alguma informação."""
    for valor in dict_dados.values():
        if isinstance(valor, str):
            if len(valor) > 0:
                return True
        else:
            return True
    return False


def manipula_dados_endereco(
        dict_endereco: Dict[str, str],
        id_pais: int,
        conn,
        tabelas_colunas
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
    uf = ''.join(dict_endereco['uf'].split()).upper()
    id_uf = verifica_preenche_valor(
        tabela_busca='endereco_unidade_federativa', coluna_busca='nome',
        valor_busca=uf, relacao_externa={'id_pais': id_pais}, conn=conn,
        list_colunas=tabelas_colunas['endereco_unidade_federativa'][:])

    municipio = ' '.join(dict_endereco['municipio'].split()).title()
    id_municipio = verifica_preenche_valor(
        tabela_busca='endereco_municipios', coluna_busca='nome',
        valor_busca=municipio, relacao_externa={'id_uf': id_uf}, conn=conn,
        list_colunas=tabelas_colunas['endereco_municipios'][:])

    bairro = ' '.join(dict_endereco['bairro'].split()).title()
    id_bairro = verifica_preenche_valor(
        tabela_busca='endereco_bairros', coluna_busca='nome',
        valor_busca=bairro, relacao_externa={'id_municipio': id_municipio},
        conn=conn, list_colunas=tabelas_colunas['endereco_bairros'][:])

    endereco = {
        'endereco': ' '.join(dict_endereco['endereco'].split()).title(),
        'cep': dict_endereco['cep'],
        'id_bairro': id_bairro,
        'id_municipio': id_municipio,
        'id_uf': id_uf,
        'id_pais': id_pais,
        'numero': dict_endereco['numero'],
        'complemento': ' '.join(dict_endereco['complemento']
                                .split()).title()
    }
    return endereco


if __name__ == "__main__":
    pass
