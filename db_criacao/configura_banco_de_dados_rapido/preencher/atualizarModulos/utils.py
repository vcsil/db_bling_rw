#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 21:04:27 2024.

@author: vcsil
"""
from preencherModulos.utils import db_pega_um_elemento
from tqdm import tqdm
import logging

log = logging.getLogger(__name__)


def api_pega_todos_id_verifica_db(api, db, param, tabela_busca,
                                  coluna_busca, colunas_retorno,
                                  conn):
    """
    Pega todos o ID de de um determinado canal da API.

    Use o limite_pag para determinar até qual página ir.

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