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
    db_inserir_varias_linhas, api_pega_todos_id, db_inserir_uma_linha,
    db_pega_varios_elementos)

from atualizarModulos.utils import solicita_novos_ids, solicita_item_novos

from colorama import Back, Style
from datetime import datetime
from tqdm import tqdm
import logging

log = logging.getLogger('root')

# =-=-=-=-=-=-=-=-=-=-=-=-=- Atualizar Tabela Contas =-=-=-=-=-=-=-=-=-=-=-=-=-


class AtualizarContas():
    """Atualiza módulo de contas."""

    def __init__(self, tabelas_colunas, db):
        self.tabelas_colunas = tabelas_colunas
        self.db = db

    def atualizar_contas_situacao(self, tabela, conn, id_situacao):
        """Atualiza a tabela produtos_tipos da database."""
        log.info(f"Atualiza situação contas receber com id {id_situacao}")
        colunas = self.tabelas_colunas[tabela][:]

        valores = {"id": id_situacao, "nome": str(id_situacao)}

        db_inserir_uma_linha(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)

    def atualizar_tipos_pagamento(self, tabela, conn, id_tipo_pag):
        """Atualiza a tabela produtos_tipos da database."""
        log.info(f"Atualiza tipos de pagamento {id_tipo_pag}")
        colunas = self.tabelas_colunas[tabela][:]

        valores = {"id": id_tipo_pag, "nome": str(id_tipo_pag)}

        db_inserir_uma_linha(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)

    def atualizar_formas_pagamento_padrao(self, tabela, conn, id_fp_padrao):
        """Atualiza a tabela formas_pagamento_padrao da database."""
        log.info(f"Atualiza padrões de pagamento {id_fp_padrao}")
        colunas = self.tabelas_colunas[tabela][:]

        valores = {"id": id_fp_padrao, "nome": str(id_fp_padrao)}

        db_inserir_uma_linha(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)

    def atualizar_formas_pagamento_destino(self, tabela, conn, id_fp_destino):
        """Atualiza a tabela formas_pagamento_destino da database."""
        log.info(f"Atualiza destino de pagamento {id_fp_destino}")
        colunas = self.tabelas_colunas[tabela][:]

        valores = {"id": id_fp_destino, "nome": str(id_fp_destino)}

        db_inserir_uma_linha(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)

    def atualizar_formas_pagamento_finalidade(self, tabela, conn, if_fp_fin):
        """Atualiza a tabela formas_pagamento_finalidade da database."""
        log.info(f"Insere finalidade de pagamento {if_fp_fin}")
        colunas = self.tabelas_colunas[tabela][:]

        valores = {"id": if_fp_fin, "nome": str(if_fp_fin)}

        db_inserir_uma_linha(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)

    def atualizar_formas_pagamento(self, tabela: str, conn, api):
        """Atualiza a tabela formas_pagamento da database."""
        colunas = self.tabelas_colunas[tabela][:]

        ids_formas_pagamento = solicita_novos_ids(
            param="/formas-pagamentos?", tabela_busca=tabela,
            coluna_busca="id_bling", coluna_retorno="id_bling", conn=conn,
            api=api, db=self.db)

        if len(ids_formas_pagamento) == 0:
            return

        print(Back.GREEN + f"Insere {len(ids_formas_pagamento)} formas pag."
              + Style.RESET_ALL)
        ROTA = '/formas-pagamentos/'
        log.info(f"Passará por {len(ids_formas_pagamento)} formas pagamentos")
        for idFormaPagamento in tqdm(ids_formas_pagamento,
                                     desc="Busca formas pag."):
            log.info(f"Solicita dados da forma pag {idFormaPagamento} na API")
            forma_pagamento = solicita_formas_pagamento(
                rota=ROTA+f"{idFormaPagamento}", api=api)

            log.info("Insere formas de pagamento")
            db_inserir_uma_linha(
                tabela=tabela, colunas=colunas, valores=forma_pagamento,
                db=self.db,  conn=conn)

        log.info("Fim de atualizar formas de pagamento")

    def atualizar_contas_contabeis(self, tabela: str, conn, api):
        """Atualiza a tabela contas_contabeis da database."""
        colunas = self.tabelas_colunas[tabela][:]

        PARAM = "/contas-contabeis"
        contas_contabeis = solicita_item_novos(
            param=PARAM, tabela=tabela, colunas_retorno="id_bling", conn=conn,
            api=api, db=self.db)

        if len(contas_contabeis) == 0:
            return

        print(Back.GREEN + f"Insere {len(contas_contabeis)} contas bancarias."
              + Style.RESET_ALL)
        log.info(f"Passará por {len(contas_contabeis)} contas bancarias")
        for c_contabel in tqdm(contas_contabeis, desc="Salva conta_contabeis"):
            c_contabel["id_bling"] = c_contabel.pop("id")
            c_contabel["nome"] = c_contabel.pop("descricao")

            log.info(f"Insere conta {c_contabel['id_bling']} no banco")
            db_inserir_uma_linha(
                tabela=tabela, colunas=colunas, valores=c_contabel,
                db=self.db,  conn=conn)
        log.info("Contas contáveis inseridas")

    def atualizar_categorias_receitas_despesas_tipo(self, tabela, conn, id_tp):
        """Atualiza a tabela categorias_receitas_despesas_tipo da database."""
        log.info("Atualiza tipos de categorias")
        colunas = self.tabelas_colunas[tabela][:]

        valores = {"id": id_tp, "nome": str(id_tp)}

        db_inserir_uma_linha(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)

    def atualizar_categorias_receitas_despesas(self, tabela: str, conn, api):
        """Atualiza a tabela categorias_receitas_despesas da database."""
        colunas = self.tabelas_colunas[tabela][:]

        PARAM = "/categorias/receitas-despesas?&tipo=0&situacao=0&"
        ids_categorias = solicita_novos_ids(
            param=PARAM, tabela_busca=tabela, coluna_busca="id_bling",
            coluna_retorno="id_bling", conn=conn, api=api, db=self.db)

        if len(ids_categorias) == 0:
            return

        print(Back.GREEN + f"Insere {len(ids_categorias)} categorias contas."
              + Style.RESET_ALL)
        ROTA = '/categorias/receitas-despesas/'
        log.info(f"Passará por {len(ids_categorias)} categorias")
        list_relacao_categoria = []
        for idCategoria in tqdm(ids_categorias, desc="Busca categorias"):
            log.info(f"Solicita dados da categoria {idCategoria} na API")
            rel, categoria = solicita_categeoria(rota=ROTA+f"{idCategoria}",
                                                 api=api)

            log.info("Insere categoria")
            db_inserir_uma_linha(tabela=tabela, colunas=colunas, db=self.db,
                                 valores=categoria, conn=conn)

            # Pegando informações sobre relação da categoria
            if rel:
                list_relacao_categoria.append(rel)

        log.info(f"Insere {len(list_relacao_categoria)} relacoes de categoria")
        print(f"Insere {len(list_relacao_categoria)} relacoes de categoria")
        tab_relacao = "categorias_receitas_despesas_relacao"
        colunas_relacao = self .tabelas_colunas[tab_relacao][:]
        colunas_relacao.remove("id")
        db_inserir_varias_linhas(tabela=tab_relacao,
                                 colunas=colunas_relacao, conn=conn,
                                 db=self.db, valores=list_relacao_categoria)

        log.info("Termina de atualizar categorias receitas despesas")

    def atualizar_contas_tipo_ocorrencia(self, tabela, conn, id_cto):
        """Atualiza a tabela contas_tipo_ocorrencia da database."""
        log.info("Atualiza tipos de ocorrência de contas")
        colunas = self.tabelas_colunas[tabela][:]

        valores = {"id": id_cto, "nome": str(id_cto)}

        db_inserir_varias_linhas(
            tabela=tabela, colunas=colunas, valores=valores,
            db=self.db, conn=conn)
        log.info("Fim de atualizar tipos de ocorrência de contas")

    def atualizar_vendedores(self, tabela: str, conn, api):
        """Atualiza a tabela vendedores da database."""
        colunas = self.tabelas_colunas[tabela][:]
        ids_vendedores_api = api_pega_todos_id(
            api, "/vendedores?situacaoContato=A&")
        ids_vendedores_api += api_pega_todos_id(
            api, "/vendedores?situacaoContato=I&")
        ids_vendedores_api += api_pega_todos_id(
            api, "/vendedores?situacaoContato=S&")
        ids_vendedores_api += api_pega_todos_id(
            api, "/vendedores?situacaoContato=E&")

        ids_vendedores_db = db_pega_varios_elementos(
            tabela_busca=tabela, colunas_retorno="id_bling",
            db=self.db, conn=conn)
        ids_vendedores_db = [item["id_bling"] for item in ids_vendedores_db]

        ids_vendedores = list(
            set(ids_vendedores_api) - set(ids_vendedores_db))
        ids_vendedores.sort()

        if len(ids_vendedores) == 0:
            return

        print(Back.GREEN + f"Insere {len(ids_vendedores)} vendedores."
              + Style.RESET_ALL)
        ROTA = "/vendedores/"
        log.info(f"Passará por {len(ids_vendedores)} vendedores")
        for idVendedor in tqdm(ids_vendedores, desc="Busca vendedores"):
            log.info(f"Solicita vendedor {idVendedor} na API")
            conta = solicita_vendedor(rota=ROTA+f"{idVendedor}", api=api)

            log.info("Insere conta")
            db_inserir_uma_linha(
                tabela=tabela, colunas=colunas, valores=conta,
                db=self.db,  conn=conn)

        log.info("Fim de preencher contas receitas despesas")

    def atualizar_contas_receitas_despesas(self, tabela: str, conn, api, fuso):
        """Atualiza a tabela contas_receitas_despesas da database."""
        colunas = self.tabelas_colunas[tabela][:]

        hoje = str(datetime.now(fuso).date())

        PARAM = "/contas/receber?"
        PARAM += f"tipoFiltroData=E&dataInicial={hoje}&dataFinal={hoje}&"
        contas_receber = solicita_novos_ids(
            param=PARAM, tabela_busca=tabela, coluna_busca="id_bling",
            coluna_retorno="id_bling", conn=conn, api=api, db=self.db)

        PARAM = "/contas/pagar?"
        PARAM += f"dataEmissaoInicial={hoje}&dataEmissaoFinal={hoje}&"
        contas_pagar = solicita_novos_ids(
            param=PARAM, tabela_busca=tabela, coluna_busca="id_bling",
            coluna_retorno="id_bling", conn=conn, api=api, db=self.db)

        ids_contas = [contas_receber, contas_pagar]

        if (len(contas_receber) + len(contas_pagar)) == 0:
            return

        ROTA = ["/contas/receber/", "/contas/pagar/"]
        for idx in tqdm(range(len(ROTA)), desc="Busca contas", position=0):
            print(
                Back.GREEN +
                f"Insere {len(ids_contas[idx])} {ROTA[idx]}."
                + Style.RESET_ALL)
            for idConta in tqdm(ids_contas[idx], desc=f"{ROTA[idx]}",
                                leave=True, position=1):
                log.info(f"Solicita dados da conta {idConta} na API")
                conta = solicita_conta(rota=ROTA[idx]+f"{idConta}", api=api,
                                       conn=conn, db=self.db, fuso=fuso,
                                       tabelas_colunas=self.tabelas_colunas)

                log.info("Insere conta")
                db_inserir_uma_linha(
                    tabela=tabela, colunas=colunas, valores=conta,
                    db=self.db,  conn=conn)
            conn.commit()

        log.info("Fim de preencher contas receitas despesas")

    def atualizar_modulo_contas(self, conn, api, fuso):
        """Atualizar módulo de contas."""
        log.info("Inicio")

        log.info("Inicio atualizar formas_pagamento")
        self.atualizar_formas_pagamento(
            tabela="formas_pagamento", conn=conn, api=api)

        log.info("Inicio atualizar contas_contabeis")
        self.atualizar_contas_contabeis(
            tabela="contas_contabeis", conn=conn, api=api)

        log.info("Inicio atualizar categorias_receitas_despesas")
        self.atualizar_categorias_receitas_despesas(
            tabela="categorias_receitas_despesas", conn=conn, api=api)

        log.info("Inicio atualizar vendedores")
        self.atualizar_vendedores(tabela="vendedores", conn=conn, api=api)

        log.info("Inicio atualizar contas_receitas_despesas")
        self.atualizar_contas_receitas_despesas(
            tabela="contas_receitas_despesas", conn=conn, api=api, fuso=fuso)

        log.info("Fim atualizar contas")


if __name__ == "__main__":
    pass
