#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 12:43:57 2023.

@author: vcsil
"""
from config.conexao_db import ConectaDB

from typing import List
from tqdm import tqdm
import logging

log = logging.getLogger(__name__)


class Utils(ConectaDB):
    """Funções utéis para preencher os módulos."""

    def _pega_todos_id(self, api, param: str) -> List[int]:
        """
        Pega todos o ID de todos os contatos no Bling.

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
            param += f'&pagina={pagina}&limite=100'

            dados_reduzido = api.solicita_na_api(param)['data']

            if (len(dados_reduzido)) > 0:
                for dados in dados_reduzido:
                    list_ids.append(dados['id'])

                barra_carregamento.update(1)
            else:
                tem_dados = False
            # tem_dados = False  # <<<<<<<<<<<<<<<<<

        log.info("Fim")
        return list_ids[::-1]  # Lista invertida = Ordem crescente de data
