#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 18:04:11 2024.

@author: vcsil
"""

from preencherModulos.preencherContas.utils_contas import (
    solicita_formas_pagamento, solicita_categeoria, solicita_conta,
    solicita_vendedor)
from preencherModulos.utils import (
    db_inserir_varias_linhas, db_inserir_uma_linha, db_pega_varios_elementos)

from atualizarModulos.utils import (solicita_novos_ids, solicita_item_novos,
                                    txt_fundo_verde, db_verifica_se_existe,
                                    item_com_valores_atualizados,
                                    db_atualizar_uma_linha)

from config.constants import API, DB, FUSO, TABELAS_COLUNAS
from datetime import datetime, date
from tqdm import tqdm
import logging

log = logging.getLogger("root")

# =-=-=-=-=-=-=-=-=-=-=-=-=- Atualizar Tabela Contas =-=-=-=-=-=-=-=-=-=-=-=-=-


class AtualizarContas():
    """Atualiza módulo de contas."""

    def __init__(self):
        pass

    def _atualizar_contas_situacao(self, conn, id_situacao):
        """Atualiza a tabela contas_situacao da database."""
        log.info(f"Atualiza situação contas receber com id {id_situacao}")

        tabela = "contas_situacao"
        colunas = TABELAS_COLUNAS[tabela][:]

        valor = {"id": id_situacao, "nome": str(id_situacao)}

        return db_inserir_uma_linha(tabela, colunas, valor, DB, conn)

    def _atualizar_tipos_pagamento(self, conn, id_tipo_pag):
        """Atualiza a tabela produtos_tipos da database."""
        log.info(f"Atualiza tipos de pagamento {id_tipo_pag}")

        tabela = "tipos_pagamento"
        colunas = TABELAS_COLUNAS[tabela][:]

        valor = {"id": id_tipo_pag, "nome": str(id_tipo_pag)}

        return db_inserir_uma_linha(tabela, colunas, valor, DB, conn)

    def _atualizar_formas_pagamento_padrao(self, conn, id_fp_padrao):
        """Atualiza a tabela formas_pagamento_padrao da database."""
        log.info(f"Atualiza padrões de pagamento {id_fp_padrao}")

        tabela = "formas_pagamento_padrao"
        colunas = TABELAS_COLUNAS[tabela][:]

        valor = {"id": id_fp_padrao, "nome": str(id_fp_padrao)}

        return db_inserir_uma_linha(tabela, colunas, valor, DB, conn)

    def _atualizar_formas_pagamento_destino(self, conn, id_fp_destino):
        """Atualiza a tabela formas_pagamento_destino da database."""
        log.info(f"Atualiza destino de pagamento {id_fp_destino}")

        tabela = "formas_pagamento_destino"
        colunas = TABELAS_COLUNAS[tabela][:]

        valor = {"id": id_fp_destino, "nome": str(id_fp_destino)}

        return db_inserir_uma_linha(tabela, colunas, valor, DB, conn)

    def _atualizar_formas_pagamento_finalidade(self, conn, if_fp_fin):
        """Atualiza a tabela formas_pagamento_finalidade da database."""
        log.info(f"Insere finalidade de pagamento {if_fp_fin}")

        tabela = "formas_pagamento_finalidade"
        colunas = TABELAS_COLUNAS[tabela][:]

        valor = {"id": if_fp_fin, "nome": str(if_fp_fin)}

        return db_inserir_uma_linha(tabela, colunas, valor, DB, conn)

    def atualizar_formas_pagamento(self, conn):
        """Atualiza a tabela formas_pagamento da database."""
        tabela = "formas_pagamento"
        colunas = TABELAS_COLUNAS[tabela][:]

        PARAM = "/formas-pagamentos?"
        ids_formas_pagamento = solicita_novos_ids(PARAM, tabela, "id_bling",
                                                  conn)

        if len(ids_formas_pagamento) == 0:
            return

        txt_fundo_verde(f"Insere {len(ids_formas_pagamento)} formas pag.")
        log.info(f"Passará por {len(ids_formas_pagamento)} formas pagamentos")

        ROTA = "/formas-pagamentos/"
        for idFormaPagamento in tqdm(ids_formas_pagamento, "Busca formas pag"):
            log.info(f"Solicita dados da forma pag {idFormaPagamento} na API")
            forma_pagamento = solicita_formas_pagamento(
                ROTA+f"{idFormaPagamento}", API)

            db_inserir_uma_linha(tabela, colunas, forma_pagamento, DB, conn)

        log.info("Fim de atualizar formas de pagamento")

    def atualizar_contas_contabeis(self, conn):
        """Atualiza a tabela contas_contabeis da database."""
        tabela = "contas_contabeis"
        colunas = TABELAS_COLUNAS[tabela][:]

        PARAM = "/contas-contabeis"
        contas_contabeis = solicita_item_novos(PARAM, tabela, "id_bling", conn)

        if len(contas_contabeis) == 0:
            return

        txt_fundo_verde(f"Insere {len(contas_contabeis)} contas bancarias.")
        log.info(f"Passará por {len(contas_contabeis)} contas bancarias")

        for c_contabel in tqdm(contas_contabeis, desc="Salva conta_contabeis"):
            c_contabel["id_bling"] = c_contabel.pop("id")
            c_contabel["nome"] = c_contabel.pop("descricao")

            log.info(f"Insere conta {c_contabel['id_bling']} no banco")
            db_inserir_uma_linha(tabela, colunas, c_contabel, DB, conn)
        log.info("Contas contáveis inseridas")

    def _atualizar_categorias_receitas_despesas_tipo(self, conn, id_tp):
        """Atualiza a tabela categorias_receitas_despesas_tipo da database."""
        log.info("Atualiza tipos de categorias")

        tabela = "categorias_receitas_despesas_tipo"
        colunas = TABELAS_COLUNAS[tabela][:]

        valores = {"id": id_tp, "nome": str(id_tp)}

        return db_inserir_uma_linha(tabela, colunas, valores, DB, conn)

    def atualizar_categorias_receitas_despesas(self, conn):
        """Atualiza a tabela categorias_receitas_despesas da database."""
        tabela = "categorias_receitas_despesas"
        colunas = TABELAS_COLUNAS[tabela][:]

        PARAM = "/categorias/receitas-despesas?&tipo=0&situacao=0&"
        ids_categorias = solicita_novos_ids(PARAM, tabela, "id_bling", conn)

        if len(ids_categorias) == 0:
            return

        txt_fundo_verde(f"Insere {len(ids_categorias)} categorias contas.")
        log.info(f"Passará por {len(ids_categorias)} categorias")

        ROTA = "/categorias/receitas-despesas/"
        list_relacao_categoria = []
        for idCategoria in tqdm(ids_categorias, desc="Busca categorias"):
            log.info(f"Solicita dados da categoria {idCategoria} na API")
            rel, categoria = solicita_categeoria(ROTA+f"{idCategoria}", API)

            log.info("Insere categoria")
            db_inserir_uma_linha(tabela, colunas, categoria, DB, conn)

            # Pegando informações sobre relação da categoria
            if rel:
                list_relacao_categoria.append(rel)

        log.info(f"Insere {len(list_relacao_categoria)} relacoes de categoria")

        tab_relacao = "categorias_receitas_despesas_relacao"
        colunas_relacao = TABELAS_COLUNAS[tab_relacao][:]
        colunas_relacao.remove("id")
        db_inserir_varias_linhas(tab_relacao, colunas_relacao,
                                 list_relacao_categoria, DB, conn)

        log.info("Termina de atualizar categorias receitas despesas")

    def _atualizar_contas_tipo_ocorrencia(self, conn, id_cto):
        """Atualiza a tabela contas_tipo_ocorrencia da database."""
        log.info("Atualiza tipos de ocorrência de contas")

        tabela = "contas_tipo_ocorrencia"
        colunas = TABELAS_COLUNAS[tabela][:]

        valor = {"id": id_cto, "nome": str(id_cto)}

        return db_inserir_varias_linhas(tabela, colunas, valor, DB, conn)

    def atualizar_vendedores(self, conn):
        """Atualiza a tabela vendedores da database."""
        log.info("Inicia atualização dos vendedores")

        tabela = "vendedores"
        colunas = TABELAS_COLUNAS[tabela][:]

        ROTA = "/vendedores?situacaoContato=T&"
        ids_vendedores_api = solicita_novos_ids(ROTA, tabela, "id_bling", conn)

        ids_vendedores_db = db_pega_varios_elementos(tabela, "id_bling", DB,
                                                     conn)
        ids_vendedores_db = [item["id_bling"] for item in ids_vendedores_db]

        ids_vendedores = list(
            set(ids_vendedores_api) - set(ids_vendedores_db))
        ids_vendedores.sort()

        if len(ids_vendedores) == 0:
            return

        txt_fundo_verde(f"Insere {len(ids_vendedores)} vendedores.")
        log.info(f"Passará por {len(ids_vendedores)} vendedores")

        ROTA = "/vendedores/"
        for idVendedor in tqdm(ids_vendedores, desc="Busca vendedores"):
            log.info(f"Solicita vendedor {idVendedor} na API")
            conta = solicita_vendedor(ROTA+f"{idVendedor}", API)

            log.info("Insere conta")
            db_inserir_uma_linha(tabela, colunas, conta, DB, conn)

    def atualizar_contas_receitas_despesas(self, conn):
        """Atualiza a tabela contas_receitas_despesas da database."""
        log.info("Inicia atualização de contas receitas despesas")

        tabela = "contas_receitas_despesas"
        colunas = TABELAS_COLUNAS[tabela][:]

        hoje = str(datetime.now(FUSO).date())

        PARAM = "/contas/receber?"
        PARAM += f"tipoFiltroData=E&dataInicial={hoje}&dataFinal={hoje}&"
        contas_receber = solicita_novos_ids(PARAM, tabela, "id_bling", conn)

        PARAM = "/contas/pagar?"
        PARAM += f"dataEmissaoInicial={hoje}&dataEmissaoFinal={hoje}&"
        contas_pagar = solicita_novos_ids(PARAM, tabela, "id_bling", conn)

        ids_contas = [contas_receber, contas_pagar]

        if (len(contas_receber) + len(contas_pagar)) == 0:
            return

        ROTA = ["/contas/receber/", "/contas/pagar/"]
        for idx in tqdm(range(len(ROTA)), desc="Busca contas"):
            txt_fundo_verde(f"Insere {len(ids_contas[idx])} {ROTA[idx]}.")

            for idConta in tqdm(ids_contas[idx], desc=f"{ROTA[idx]}"):
                log.info(f"Solicita dados da conta {idConta} na API")

                conta_existe = db_verifica_se_existe(tabela, "id_bling",
                                                     idConta, conn)

                conta = solicita_conta(ROTA[idx]+f"{idConta}", API,
                                       TABELAS_COLUNAS, conn, DB, FUSO)

                parametros = ['vencimento', 'data_emissao',
                              'vencimento_original', 'competencia']
                for p in parametros:
                    data = conta[p].split("-")
                    conta[p] = date(int(data[0]), int(data[1]), int(data[2]))

                if conta_existe:
                    conta_modificada = item_com_valores_atualizados(conta,
                                                                    tabela,
                                                                    "id_bling",
                                                                    conn)
                    if conta_modificada:
                        db_atualizar_uma_linha(tabela, colunas,
                                               conta_modificada,
                                               "id_bling", idConta, conn)
                        continue
                    else:
                        continue

                log.info("Insere conta")
                db_inserir_uma_linha(tabela, colunas, conta, DB, conn)
            conn.commit()

        log.info("Fim de preencher contas receitas despesas")

    def atualizar_modulo_contas(self, conn):
        """Atualizar módulo de contas."""
        log.info("Inicio")

        log.info("Inicio atualizar formas_pagamento")
        self.atualizar_formas_pagamento(conn)

        log.info("Inicio atualizar contas_contabeis")
        self.atualizar_contas_contabeis(conn)

        log.info("Inicio atualizar categorias_receitas_despesas")
        self.atualizar_categorias_receitas_despesas(conn)

        log.info("Inicio atualizar vendedores")
        self.atualizar_vendedores(conn)

        log.info("Inicio atualizar contas_receitas_despesas")
        self.atualizar_contas_receitas_despesas(conn)

        log.info("Fim atualizar contas")


if __name__ == "__main__":
    pass
