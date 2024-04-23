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
from atualizarModulos.utils import solicita_item_novos, txt_fundo_verde

from config.constants import FUSO, TABELAS_COLUNAS
from datetime import datetime
from tqdm import tqdm
import logging

log = logging.getLogger('root')

# =-=-=-=-=-=-=-=-=-=-=-=-= Atualizar Tabela Contatos =-=-=-=-=-=-=-=-=-=-=-=-=


class AtualizarVendas():
    """Atualiza módulo de produtos."""

    def __init__(self):
        pass

    def atualizar_modulos(self, conn):
        """Atualiza a tabela modulos da database."""
        log.info("Atualiza módulos")

        tabela = "modulos"
        colunas = TABELAS_COLUNAS[tabela][:]

        PARAM = "/situacoes/modulos"
        modulos = solicita_item_novos(PARAM, tabela, "id_bling", conn)

        list_ids_modulos = []

        if len(modulos) == 0:
            return []

        txt_fundo_verde(f"Insere {len(modulos)} módulos pedidos.")
        log.info(f"Passará por {len(modulos)} módulos")

        for modulo in tqdm(modulos, desc="Salva modulos"):
            modulo["id_bling"] = modulo.pop("id")
            modulo["criar_situacoes"] = modulo.pop("criarSituacoes")
            list_ids_modulos.append(modulo["id_bling"])

            log.info(f"Insere módulo {modulo['id_bling']} no banco de dados")
            db_inserir_uma_linha(tabela, colunas, modulo, conn)

        return list_ids_modulos

    def atualizar_situacoes(self, ids_modulos: list, conn):
        """Atualiza a tabela situacoes da database."""
        log.info("Atualiza situacoes")

        tabela = "situacoes"
        colunas = TABELAS_COLUNAS[tabela][:]

        # Pega os módulos novos e os já salvos
        ids_modulos_db = db_pega_varios_elementos("modulos", "id_bling", conn)
        ids_modulos += [item["id_bling"] for item in ids_modulos_db]

        log.info(f"Passará por {len(ids_modulos)} módulos")
        for id_modulo in tqdm(ids_modulos, desc="Modulo de pedidos"):
            PARAM = f"/situacoes/modulos/{id_modulo}"
            situacoes = solicita_item_novos(PARAM, tabela, "id_bling", conn)

            if len(situacoes) == 0:
                continue

            txt_fundo_verde(f"Insere {len(situacoes)} situações.")
            log.info(f"Passará por {len(situacoes)} situações")

            for situacao in situacoes:
                situacao["id_bling"] = situacao.pop("id")
                situacao["id_modulo"] = id_modulo
                situacao.pop("idHerdado")

                log.info(f"Insere situacao {situacao['id_bling']}")
                db_inserir_uma_linha(tabela, colunas, situacao, conn)

        log.info("Situações atualizadas")

    def _atualizar_transporte_frete_por_conta_de(self, conn, id_trans):
        """Atualiza a tabela transporte_frete_por_conta_de da database."""
        log.info("Atualiza transporte frete por conta de")

        tabela = "transporte_frete_por_conta_de"
        colunas = TABELAS_COLUNAS[tabela][:]

        valor = {"id": id_trans, "nome": str(id_trans)}

        db_inserir_uma_linha(tabela, colunas, valor, conn)

    def atualizar_pedidos_vendas(self, conn):
        """Atualiza a tabela vendas da database."""
        hoje = str(datetime.now(FUSO).date())
        PARAM = f"/pedidos/vendas?dataAlteracaoInicial={hoje}&"
        ids_vendas_alter = api_pega_todos_id(PARAM)
        ids_vendas_alter.sort()

        if len(ids_vendas_alter) == 0:
            return

        txt_fundo_verde(f"Insere/altera {len(ids_vendas_alter)} pedidos.")

        ROTA = "/pedidos/vendas/"
        for id_venda in tqdm(ids_vendas_alter, desc="Busca pedidos de vendas"):
            log.info(f"Solicita dados da venda {id_venda} na API")

            solicita_preenche_venda(ROTA+f"{id_venda}", conn)
            conn.commit()

        log.info("Fim de atualizar pedido de venda")

    def atualizar_modulo_vendas(self, conn):
        """Atualizar módulo de produtos."""
        log.info("Inicio atualização vendas")

        log.info("Inicio atualizar modulos")
        modulos = self.atualizar_modulos(conn)

        log.info("Inicio atualizar situações")
        self.atualizar_situacoes(modulos, conn)

        log.info("Inicio atualizar vendas")
        self.atualizar_pedidos_vendas(conn)

        log.info("Fim produtos")


if __name__ == "__main__":
    pass
