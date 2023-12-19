#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 11:11:39 2023.

@author: vcsil
"""
from config.conexao_db import ConectaDB

from typing import Dict, Union
from datetime import datetime
import logging

log = logging.getLogger(__name__)


class UtilsContatos(ConectaDB):
    """Funções utéis para preencher contatos."""

    def _manipula_dados_contatos(self, contato: dict, fuso,
                                 conn, tabelas_colunas):

        contato_info = {
            'id_bling': contato['id'],
            'nome': (contato['nome'].split()[0]).title(),
            'sobrenome': ' '.join(contato['nome'].split()[1:]).title(),
            'codigo': contato['codigo'],
            'id_situacao_contato': self._pega_id_elemento(tabelas_colunas,
                                                          contato['situacao'],
                                                          'contatos_situacao',
                                                          'sigla', conn),
            'numero_documento': contato['numeroDocumento'],
            'telefone': self._formata_numero_telcel(contato['telefone']),
            'celular': self._formata_numero_telcel(contato['celular']),
            'fantasia': contato['fantasia'],
            'id_tipo_contato': self._pega_id_elemento(tabelas_colunas,
                                                      contato['tipo'],
                                                      'contatos_tipo',
                                                      'sigla', conn,),
            'id_indicador_inscricao_estadual': contato['indicadorIe'],
            'inscricao_estadual': contato['ie'],
            'rg': contato['rg'],
            'orgao_emissor': contato['orgaoEmissor'],
            'email': contato['email'],
            'data_nascimento': (
                self._formata_data(contato['dadosAdicionais']
                                   ['dataNascimento'])),
            'sexo': self._formata_sexo(contato['dadosAdicionais']['sexo']),
            'id_classificacao_contato': (self.
                                         _formata_classificacao(
                                             contato['tiposContato'])),
            'cliente_desde': datetime.now(fuso)
        }
        for chave, valor in contato_info.items():
            if (valor == ''):
                if (chave != "sobrenome"):
                    contato_info[chave] = None

        log.info("Fim")
        return contato_info

    def _pega_id_elemento(
            self,
            tabelas_colunas,
            elemento: str,
            tabela: str,
            coluna_busca: str,
            conn
    ) -> int:
        """
        Utilizado para buscar o id de elementos qualificadores que já existem.

        Parameters
        ----------
        elemento : str
            O dado em sim.
        tabela : str
            Tabela localizada.
        coluna_busca : str
            Coluna para fazer a busca.

        Returns
        -------
        int
            id do dado na tabela.

        """
        try:
            elemento_dict = self.select_one_from_db(
                tabela=tabela, conn=conn, colunas=tabelas_colunas[tabela],
                filtro=(f"WHERE {coluna_busca} =", elemento))

            for key in elemento_dict.keys():
                if (key == 'id') or (key == "id_bling"):
                    return elemento_dict[key]
        except AttributeError as e:
            print(f"O elemento '{elemento}' não existe na tabela '{tabela}'")
            print(f"nem na coluna '{tabela}.{coluna_busca}'. : {e}'")

    def _formata_numero_telcel(self, numero_string: str) -> str:
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

    def _formata_data(self, data_bling: str):
        if data_bling == '0000-00-00':
            return None
        data_bling = data_bling.split('-')  # AAAA-MM-DD
        data_bling = list(map(int, data_bling))
        data = datetime(year=data_bling[0],
                        month=data_bling[1],
                        day=data_bling[2])
        return data

    def _formata_sexo(self, sexo_bling: str):
        sexo_bling = sexo_bling.upper()
        if (sexo_bling == 'F') or (sexo_bling == ''):
            return 2
        elif sexo_bling == 'M':
            return 1
        else:
            return 3

    def _formata_classificacao(self, tipo_contato: list):
        if tipo_contato:
            return tipo_contato[0]['id']
        else:
            return 14572462908  # Cliente

    def _regra_pais(self, tipo_contato: str, pais: str) -> str:
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

    def _possui_informacao(
            self,
            dict_dados: Dict[str, Union[str, int, None]]
    ) -> bool:
        """Verifica se dict contém alguma informação."""
        for valor in dict_dados.values():
            if isinstance(valor, str):
                if len(valor) > 0:
                    return True
            else:
                return True
        return False

    def _preencher_campos_endereco(
            self,
            tabela: str,
            campo: str,
            campo_nome: str,
            conn,
            tabelas_colunas,
            relacao_externa: Dict[str, int] = None
    ) -> int:
        """
        Confere e insere dados referente ao endereco.

        Verifica se dado já existe no banco de dados e retorna id

        Parameters
        ----------
        tabela : str
            Tabela para buscar/inserir o dado.
        campo : str
            Campo referente ao nome da coluna da tabela do banco de dados.
        campo_nome : str
            Valor a ser inserido no campo.
        relacao_externa : Dict[str, int]
            Dict com nome da coluna de relação e o respectivo id.

        Returns
        -------
        id do campo: int

        """
        colunas = tabelas_colunas[tabela][:]
        colunas.remove('id')

        # Procura ID do campo
        campo_ja_existe = self.select_one_from_db(
            tabela=tabela, colunas='id', conn=conn,
            filtro=(f"WHERE {campo} =", campo_nome)
        )
        if campo_ja_existe:
            return campo_ja_existe['id']
        else:
            valores = {campo: campo_nome}
            # Adicona relações
            if relacao_externa:
                valores = {**valores, **{chave: valor
                                         for chave, valor
                                         in relacao_externa.items()}}

            dados_inseridos = self.insert_one_in_db(
                tabela=tabela, colunas=colunas, valores=valores,
                valores_placeholder=colunas, conn=conn
            )
            return dados_inseridos['id']

    def _manipula_dados_endereco(
            self,
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
        id_uf = self._preencher_campos_endereco(
            tabela='endereco_unidade_federativa', campo='nome', campo_nome=uf,
            relacao_externa={'id_pais': id_pais}, conn=conn,
            tabelas_colunas=tabelas_colunas)

        municipio = ' '.join(dict_endereco['municipio'].split()).title()
        id_municipio = self._preencher_campos_endereco(
            tabela='endereco_municipios', campo='nome', campo_nome=municipio,
            relacao_externa={'id_uf': id_uf}, conn=conn,
            tabelas_colunas=tabelas_colunas)

        bairro = ' '.join(dict_endereco['bairro'].split()).title()
        id_bairro = self._preencher_campos_endereco(
            tabela='endereco_bairros', campo='nome', campo_nome=bairro,
            relacao_externa={'id_municipio': id_municipio}, conn=conn,
            tabelas_colunas=tabelas_colunas)

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
