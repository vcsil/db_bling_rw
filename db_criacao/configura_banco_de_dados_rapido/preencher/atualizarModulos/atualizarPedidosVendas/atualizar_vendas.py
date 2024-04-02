#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 14:09:44 2024.

@author: vcsil
"""

from preencherModulos.utils import (
    db_inserir_uma_linha, api_pega_todos_id, db_pega_varios_elementos)

from atualizarModulos.atualizarPedidosVendas.utils_vendas import (
    solicita_preenche_venda)
from atualizarModulos.utils import solicita_item_novos

from colorama import Back, Style
from datetime import datetime
from tqdm import tqdm
import logging

log = logging.getLogger('root')

# =-=-=-=-=-=-=-=-=-=-=-=-= Atualizar Tabela Contatos =-=-=-=-=-=-=-=-=-=-=-=-=


class AtualizarVendas():
    """Atualiza módulo de produtos."""

    def __init__(self, tabelas_colunas, db):
        self.tabelas_colunas = tabelas_colunas
        self.db = db

    def atualizar_modulos(self, tabela: str, conn, api):
        """Atualiza a tabela modulos da database."""
        log.info("Atualiza módulos")
        colunas = self.tabelas_colunas[tabela][:]

        PARAM = "/situacoes/modulos"
        modulos = solicita_item_novos(
            param=PARAM, tabela=tabela, colunas_retorno="id_bling", conn=conn,
            api=api, db=self.db)

        list_ids_modulos = []

        if len(modulos) == 0:
            return []

        print(Back.GREEN + f"Insere {len(modulos)} módulos pedidos."
              + Style.RESET_ALL)
        log.info(f"Passará por {len(modulos)} módulos")
        for modulo in tqdm(modulos, desc="Salva modulos"):
            modulo["id_bling"] = modulo.pop("id")
            modulo["criar_situacoes"] = modulo.pop("criarSituacoes")
            list_ids_modulos.append(modulo["id_bling"])

            log.info(f"Insere módulo {modulo['id_bling']} no banco de dados")
            db_inserir_uma_linha(
                tabela=tabela, colunas=colunas, valores=modulo,
                db=self.db,  conn=conn)
        log.info("Módulos inseridos")
        return list_ids_modulos

    def atualizar_situacoes(self, ids_modulos: list, tabela: str, conn, api):
        """Atualiza a tabela situacoes da database."""
        log.info("Atualiza situacoes")
        colunas = self.tabelas_colunas[tabela][:]

        # Pega os módulos novos e os já salvos
        ids_modulos_db = db_pega_varios_elementos(
            tabela_busca="modulos", colunas_retorno="id_bling",
            conn=conn, db=self.db)
        ids_modulos += [item["id_bling"] for item in ids_modulos_db]

        log.info(f"Passará por {len(ids_modulos)} módulos")
        for id_modulo in tqdm(ids_modulos, desc="Modulo de pedidos"):
            PARAM = f"/situacoes/modulos/{id_modulo}"
            situacoes = solicita_item_novos(
                param=PARAM, tabela=tabela, colunas_retorno="id_bling",
                conn=conn, api=api, db=self.db)

            if len(situacoes) == 0:
                continue

            print(Back.GREEN + f"Insere {len(situacoes)} situações."
                  + Style.RESET_ALL)
            log.info(f"Passará por {len(situacoes)} situações")
            for situacao in situacoes:
                situacao["id_bling"] = situacao.pop("id")
                situacao["id_modulo"] = id_modulo
                situacao.pop("idHerdado")

                log.info(f"Insere situacao {situacao['id_bling']}")
                db_inserir_uma_linha(
                    tabela=tabela, colunas=colunas, valores=situacao,
                    db=self.db,  conn=conn)
        log.info("Situações atualizadas")

    def atualizar_transporte_frete_por_conta_de(self, tabela, conn, id_trans):
        """Atualiza a tabela produtos_formatos da database."""
        log.info("Atualiza transporte frete por conta de")
        colunas = self.tabelas_colunas[tabela][:]

        valores = {"id": id_trans, "nome": str(id_trans)}

        db_inserir_uma_linha(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)
        log.info("Termina de inserir transporte frete por conta de")

    def atualizar_pedidos_vendas(self, tabela: str, conn, api, fuso):
        """Atualiza a tabela vendas da database."""
        hoje = str(datetime.now(fuso).date())
        PARAM = f"/pedidos/vendas?dataAlteracaoInicial={hoje}&"
        ids_vendas_alter = api_pega_todos_id(api, PARAM)
        ids_vendas_alter.sort()

        if len(ids_vendas_alter) == 0:
            return

        print(Back.GREEN + f"Insere/altera {len(ids_vendas_alter)} pedidos."
              + Style.RESET_ALL)
        ROTA = "/pedidos/vendas/"
        for id_venda in tqdm(ids_vendas_alter, desc="Busca pedidos de vendas"):
            log.info(f"Solicita dados da venda {id_venda} na API")
            solicita_preenche_venda(
                rota=ROTA+f"{id_venda}", api=api, conn=conn, db=self.db,
                tabelas_colunas=self.tabelas_colunas, fuso=fuso)
            conn.commit()

        log.info("Fim de atualizar pedido de venda")

    def atualizar_modulo_vendas(self, conn, api, fuso):
        """Atualizar módulo de produtos."""
        log.info("Inicio atualização vendas")

        log.info("Inicio atualizar modulos")
        modulos = self.atualizar_modulos(tabela="modulos", conn=conn, api=api)

        log.info("Inicio atualizar situações")
        self.atualizar_situacoes(tabela="situacoes", ids_modulos=modulos,
                                 api=api, conn=conn)

        log.info("Inicio atualizar vendas")
        self.atualizar_pedidos_vendas(tabela="vendas", conn=conn, api=api,
                                      fuso=fuso)

        log.info("Fim produtos")


if __name__ == "__main__":
    pass
