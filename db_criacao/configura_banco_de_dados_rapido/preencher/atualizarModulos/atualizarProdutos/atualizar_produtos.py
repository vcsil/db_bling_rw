#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 13:06:07 2023.

@author: vcsil
"""
from preencherModulos.preencherProdutos.utils_produtos import (
    solicita_categeoria, solicita_deposito, produto_insere_saldo_estoque,
    solicita_insere_variacao, solicita_produto, insere_segunda_tentativa)
from preencherModulos.utils import (
    db_inserir_varias_linhas, db_inserir_uma_linha, api_pega_todos_id,
    db_pega_varios_elementos, db_pega_varios_elementos_controi_filtro,
    db_pega_um_elemento)

from atualizarModulos.atualizarProdutos.utils_produtos import (
    atualizar_estoque_fornecedor, solicita_produto_para_atualizar,
    manipula_insere_variacao, atualiza_estoque, manipula_variacao_excluidas,
    solicita_produtos_com_midias_vencidas, solicita_ids_midias_produtos,
    manipula_midias_atualizadas, cria_atualiza_midia_produtos,
    atualiza_midia_produtos)
from atualizarModulos.utils import (
    db_atualizar_uma_linha, db_verifica_se_existe, solicita_novos_ids,
    txt_fundo_verde, slice_array, txt_fundo_azul, txt_amarelo)

from config.constants import TABELAS_COLUNAS, API
from datetime import date, timedelta
from tqdm import tqdm
import logging

log = logging.getLogger("root")

# =-=-=-=-=-=-=-=-=-=-=-=-= Preencher Tabela Produtos =-=-=-=-=-=-=-=-=-=-=-=-=


class AtualizarProdutos():
    """Preenche módulo de produtos."""

    def __init__(self, DATA_AGORA):
        self.DATA_AGORA = DATA_AGORA

    def _atualiza_produtos_tipos(self, sigla, conn):
        """Atualiza a tabela produtos_tipos da database."""
        log.info("Insere novos tipos de contatos")

        tabela = "produtos_tipos"
        colunas = TABELAS_COLUNAS[tabela][:]
        colunas.remove("id")

        valor = {"nome": sigla, "sigla": sigla}

        return db_inserir_uma_linha(tabela, colunas, valor, conn)

    def _atualiza_produtos_formatos(self, sigla, conn):
        """Atualiza a tabela produtos_formatos da database."""
        log.info("Insere novo formato de produtos")

        tabela = "produtos_formatos"
        colunas = TABELAS_COLUNAS[tabela][:]
        colunas.remove("id")

        valor = {"nome": sigla, "sigla": sigla}

        return db_inserir_uma_linha(tabela, colunas, valor, conn)

    def _atualiza_produtos_tipo_producao(self, sigla, conn):
        """Atualiza a tabela produtos_tipo_producao da database."""
        log.info("Insere novos tipos de produção de produtos")

        tabela = "produtos_tipo_producao"
        colunas = TABELAS_COLUNAS[tabela][:]
        colunas.remove("id")

        valor = {"nome": sigla, "sigla": sigla},

        return db_inserir_uma_linha(tabela, colunas, valor, conn)

    def _atualiza_produtos_condicao(self, id_condicao, conn):
        """Atualiza a tabela produtos_condicao da database."""
        log.info("Insere nova condicao de produtos")

        tabela = "produtos_condicao"
        colunas = TABELAS_COLUNAS[tabela][:]

        valor = {"id": id_condicao, "nome": str(id_condicao)},

        return db_inserir_uma_linha(tabela, colunas, valor, conn)

    def _atualiza_produtos_categorias(self, conn):
        """Atualiza a tabela produtos_categorias da database."""
        log.info("Insere novas categorias de produtos.")

        tabela = "produtos_categorias"
        colunas = TABELAS_COLUNAS[tabela][:]

        PARAM = "/categorias/produtos?"
        ids_categorias = solicita_novos_ids(PARAM, tabela, "id_bling", conn)

        if len(ids_categorias) == 0:
            return
        txt_fundo_verde(f"Insere {len(ids_categorias)} catg. produtos novas")

        ROTA = "/categorias/produtos/"
        list_relacao_categoria = []
        for idCategoria in tqdm(ids_categorias, desc="Atualiza categorias",
                                position=1):
            log.info(f"Solicita dados da categoria {idCategoria} na API")
            rel, categoria = solicita_categeoria(ROTA+f"{idCategoria}")

            log.info(f"Insere categoria {idCategoria}")
            db_inserir_uma_linha(tabela, colunas, categoria, conn)

            # Pegando informações sobre relação da categoria
            if rel:
                list_relacao_categoria.append(rel)

        log.info("Insere relacoes das categorias")
        colunas_relacao = TABELAS_COLUNAS[tabela + "_relacao"][:]
        colunas_relacao.remove("id")
        db_inserir_varias_linhas(tabela + "_relacao", colunas_relacao,
                                 valores=list_relacao_categoria, conn=conn)

    def _atualiza_produtos_depositos(self, conn):
        """Atualiza a tabela produtos_depositos da database."""
        log.info("Insere novas categorias de produtos.")

        tabela = "produtos_depositos"
        colunas = TABELAS_COLUNAS[tabela][:]

        PARAM = "/depositos?"
        ids_depositos = solicita_novos_ids(PARAM, tabela, "id_bling", conn)

        if len(ids_depositos) == 0:
            return

        txt_fundo_verde(f"Insere {len(ids_depositos)} depositos novos")
        log.info(f"Passará por {len(ids_depositos)} depositos")

        ROTA = "/depositos/"
        for idDeposito in tqdm(ids_depositos, desc="Busca depositos",
                               position=1):
            deposito = solicita_deposito(ROTA+f"{idDeposito}")

            log.info(F"Insere deposito {idDeposito} NO db")
            db_inserir_uma_linha(tabela, colunas, deposito, conn)

        log.info("Fim de atualizar produtos depositos")

    def atualiza_produtos_novos(self, conn):
        """Insere produtos novos, cadastrados recentemente. Compara os ID."""
        tabela = "produtos"

        PARAM = "/produtos?criterio=5&tipo=T&"
        # Pega todos os produtos Pai e Simples
        ids_produtos = solicita_novos_ids(PARAM, tabela, "id_bling", conn)

        if len(ids_produtos) == 0:
            return

        txt_fundo_verde(f"Insere {len(ids_produtos)} produtos novos")
        log.info(f"Passará por {len(ids_produtos)} produtos")

        produtos_nao_incluidos = []
        for idProduto in tqdm(ids_produtos, desc="Busca produtos", position=1):
            log.info(f"Solicita dados do produto {idProduto} na API")
            variacoes, produto = solicita_produto(idProduto, conn,
                                                  inserir_produto=True)

            # Se o produto não for Pai, será resolvido depois.
            if not produto:
                produtos_nao_incluidos.append(variacoes)
                log.info(f"Produto {idProduto} não incluido de primeira.")
                continue

            # Lida com as variações do produto Pai
            if variacoes:
                for variacao in variacoes:
                    solicita_insere_variacao(variacao, idProduto, conn)

                    produto_insere_saldo_estoque(variacao["id"], conn)
            else:
                produto_insere_saldo_estoque(idProduto, conn)
            conn.commit()

        ids_produtos_prontos = db_pega_varios_elementos(tabela, "id_bling",
                                                        conn)
        ids_produtos_prontos = [linha["id_bling"] for linha
                                in ids_produtos_prontos]

        ids_produtos_nao_incluidos = [item["id"] for item
                                      in produtos_nao_incluidos]

        log.info(f"Passará por {len(produtos_nao_incluidos)} produtos, novame")
        for prod_variacao in tqdm(produtos_nao_incluidos, desc="Repete busca",
                                  position=1):
            if prod_variacao["id"] in ids_produtos_prontos:
                ids_produtos_nao_incluidos.remove(prod_variacao["id"])
                continue
            insere_segunda_tentativa(prod_variacao, conn)

        txt_amarelo(f"Produtos não incluidos: {ids_produtos_nao_incluidos}")

    def atualiza_valores_produtos(self, conn):
        """Busca por produtos que foram alterado na data definida."""
        tabela = "produtos"
        colunas = TABELAS_COLUNAS[tabela][:]
        colunas.remove("criado_em")

        # Pega os produtos alterados no dia de hoje
        hoje = str(self.DATA_AGORA.date())
        param = "/produtos?criterio=1&tipo=P&"
        param += f"dataAlteracaoInicial={hoje}&dataAlteracaoFinal={hoje}&"
        ids_produtos_alterado = api_pega_todos_id(param)

        if len(ids_produtos_alterado) == 0:
            return

        txt_fundo_azul(f"Atualiza {len(ids_produtos_alterado)} produtos")

        for idProduto in tqdm(ids_produtos_alterado, desc="Atualiza produtos",
                              position=1):
            log.info(f"Atualiza o produto: {idProduto}.")
            # Verifica se ele já existe no banco de dados
            produto_existe = db_verifica_se_existe(tabela, "id_bling",
                                                   idProduto, conn)

            log.info(f"Solicita dados do produto {idProduto} na API")
            if produto_existe:
                # Atualiza somente produtos com valores atualizados
                variacoes, produto = solicita_produto_para_atualizar(idProduto,
                                                                     conn)
                if produto:
                    db_atualizar_uma_linha(tabela, colunas, produto,
                                           ["id_bling"], [idProduto], conn)

                # A verificação não lida no caso do produto ter recebido novas
                # imagens. Portanto vamos fazer uma busca especifica.
                self.atualizar_midia(conn, [idProduto])

            else:  # Manipula e insere
                variacoes, produto = solicita_produto(idProduto, conn,
                                                      inserir_produto=True)

            if variacoes:
                # Verifica a situação das variaçoes
                ids_variacao = manipula_variacao_excluidas(idProduto,
                                                           variacoes, conn)

                # Lida com as variações do produto Pai
                ids_variacao += manipula_insere_variacao(idProduto, variacoes,
                                                         conn)

                # A verificação não lida no caso do produto ter recebido novas
                # imagens. Portanto vamos fazer uma busca especifica.
                self.atualizar_midia(conn, ids_variacao)
            else:
                # Caso seja produto sem variação, lida com o estoque.
                if produto_existe:
                    atualizar_estoque_fornecedor(idProduto, conn)
                else:
                    produto_insere_saldo_estoque(idProduto, conn)

            conn.commit()

    def atualizar_estoque(self, conn):
        """Utiliado para atualizar a quantidade de produtos em estoque."""
        BATCH_SIZE = 271

        ids_p_db = db_pega_varios_elementos_controi_filtro(
            tabela_busca="produtos",
            filtro="WHERE situacao_produto='Inativo'",
            colunas_retorno=["id_bling"], conn=conn)
        ids_produto_db = [int(linha["id_bling"]) for linha in ids_p_db]

        ids_p_db = db_pega_varios_elementos_controi_filtro(
            tabela_busca="produtos",
            filtro="WHERE situacao_produto='Excluido'",
            colunas_retorno=["id_bling"], conn=conn)
        ids_produto_db += [int(linha["id_bling"]) for linha in ids_p_db]

        ids_pe_db = db_pega_varios_elementos(
            tabela_busca="produtos_estoques", colunas_retorno="id_produto",
            conn=conn)
        ids_pe_db = [int(linha["id_produto"]) for linha in ids_pe_db]

        ids_att_estoque = list(set(ids_pe_db) - set(ids_produto_db))
        ids_att_estoque.sort()
        ids_att_estoque = [str(id_prod) for id_prod in ids_att_estoque]
        batchs = slice_array(ids_att_estoque, BATCH_SIZE)

        for batch in tqdm(batchs, "Atualizando estoque de produtos",
                          position=1):
            query = "&idsProdutos[]="
            query = "idsProdutos[]=" + query.join(batch)
            param = "/estoques/saldos?" + query
            list_estoque_produtos = API.solicita_na_api(param)["data"]

            for saldo_estoque in tqdm(list_estoque_produtos, "Att produtos.",
                                      position=1):
                atualiza_estoque(saldo_estoque, conn)

        return

    def atualizar_midia(self, conn, ids_produtos=None):
        """Atualiza as mídias que passaram da validade."""
        tabela = "produtos_midias"
        colunas = TABELAS_COLUNAS[tabela][:]
        colunas.remove("criado_em")
        colunas.remove("id")

        if not (ids_produtos):
            ids_produtos = solicita_produtos_com_midias_vencidas(conn)

        for id_produto in tqdm(ids_produtos, "Atualizando midias", position=1):
            alterad = db_pega_um_elemento("produtos", "id_bling", [id_produto],
                                          "alterado_em", conn)["alterado_em"]
            if alterad:
                diferenca_tempo = self.DATA_AGORA - alterad
                if (diferenca_tempo < timedelta(hours=6)):
                    continue

            # Solicita o produto na api e pega as mídias atualizadas.
            produto_api = API.solicita_na_api(f"/produtos/{id_produto}")
            midias_api = produto_api["data"]["midia"]

            # Formata as mídias atualizadas:
            imagens_api = manipula_midias_atualizadas(conn, id_produto,
                                                      midias_api["imagens"])
            if not imagens_api:
                continue

            # Solicida mídias salvas no banco de dados.
            ids_midias_db = solicita_ids_midias_produtos(conn, id_produto)

            # Se tiver mais mídias novas do que no bd vai ser preciso criar
            if len(imagens_api) > len(ids_midias_db):
                cria_atualiza_midia_produtos(conn, imagens_api, ids_midias_db,
                                             id_produto)
                continue

            atualiza_midia_produtos(conn, imagens_api, ids_midias_db,
                                    id_produto)
            conn.commit()

        return

    def atualizar_modulo_produtos(self, conn):
        """Preencher módulo de produtos."""
        log.info("Inicio")

        log.info("Inicio atualizar categroias de produtos")
        self._atualiza_produtos_categorias(conn=conn)

        log.info("Inicio atualizar depositos de produtos")
        self._atualiza_produtos_depositos(conn=conn)
        conn.commit()

        log.info("Inicio inserir novos produtos")
        self.atualiza_produtos_novos(conn=conn)

        log.info("Inicio atualizar valores de produtos")
        self.atualiza_valores_produtos(conn=conn)
        conn.commit()

        self.atualizar_estoque(conn=conn)

        log.info("Inicia atualização das midias vencidas")
        self.atualizar_midia(conn)
        conn.commit()

        log.info("Fim produtos")


if __name__ == "__main__":
    pass
