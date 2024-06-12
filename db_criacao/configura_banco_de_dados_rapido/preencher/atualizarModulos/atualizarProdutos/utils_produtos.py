#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 17:30:41 2024.

@author: vcsil
"""
from preencherModulos.utils import (db_inserir_uma_linha,
                                    db_pega_varios_elementos_controi_filtro)
from preencherModulos.preencherProdutos.utils_produtos import (
    _solicita_estoque_fornecedor, produto_insere_saldo_estoque,
    solicita_produto, _solicita_variacao, _modifica_produto_estoque,
    _modifica_valores_produto)

from atualizarModulos.utils import (
    db_atualizar_uma_linha, db_verifica_se_existe, db_deletar_varias_linhas,
    item_com_valores_atualizados)

from config.constants import API, TABELAS_COLUNAS, FUSO
from datetime import datetime
import logging

log = logging.getLogger('root')


def atualizar_estoque_fornecedor(id_produto, conn):
    """Pega saldos da API e atualiza no banco de dados."""
    log.info(f"Atualiza estoque do produto {id_produto}")

    colunas_prod_est = TABELAS_COLUNAS["produtos_estoques"][:]
    colunas_prod_est.remove("id")
    colunas_prod_for = TABELAS_COLUNAS["produto_fornecedor"][:]

    # Inserir saldo de estoque
    fornecedores, estoques = _solicita_estoque_fornecedor(id_produto)

    _verifica_atualiza_valor_unico(items=estoques, tabela="produtos_estoques",
                                   colunas=colunas_prod_est,
                                   coluna_busca=["id_produto", "id_deposito"],
                                   conn=conn)

    _verifica_atualiza_valor_unico(items=fornecedores,
                                   tabela="produto_fornecedor",
                                   colunas=colunas_prod_for,
                                   coluna_busca=["id_bling"],
                                   conn=conn)


def _verifica_atualiza_valor_unico(items, tabela, colunas, coluna_busca, conn):
    """Passa por um array de itens e atualiza os itens que tem valores att."""
    for item in items:
        if "alterado_em" in item.keys():
            item.pop("alterado_em")

        valor_busca = [item[key] for key in coluna_busca]
        item_modificado = item_com_valores_atualizados(item, tabela,
                                                       coluna_busca, conn)
        if not item_modificado:
            continue

        db_atualizar_uma_linha(tabela, colunas, item_modificado, coluna_busca,
                               valor_filtro=valor_busca, conn=conn)


def solicita_produto_para_atualizar(idProduto, conn):
    """Solicita produto e retorna dict se tiver alteração ou False."""
    variacoes, produto = solicita_produto(idProduto, conn,
                                          inserir_produto=False)

    produto.pop("criado_em")
    produto_modificado = item_com_valores_atualizados(produto, "produtos",
                                                      "id_bling", conn)

    return variacoes, produto_modificado


def manipula_insere_variacao(id_pai, variacoes, conn):
    """Solicita, verifica modificações, manipula e insere variacao."""
    for variacao in variacoes:
        produto_variacao, variacao = _solicita_variacao(variacao, id_pai, conn)

        # Verifica se a variação já existe no banco de dados
        variacao_existe = db_verifica_se_existe("produtos", "id_bling",
                                                [variacao["id_bling"]], conn)
        if variacao_existe:
            produto_variacao, variacao = _solicita_variacao_para_atualizar(
               produto_variacao, variacao, conn)

            _atualiza_variacao(produto_variacao, variacao, conn)
        else:
            _cria_variacao(produto_variacao, variacao, conn)


def manipula_variacao_excluidas(id_produto, variacoes_api, conn):
    """Verifica se existe variações no banco de dados que foram excl na api."""
    tabela = "produto_variacao"
    colunas = TABELAS_COLUNAS[tabela][:]
    filtro = f"WHERE id_produto_pai='{id_produto}'"

    variacoes_db = db_pega_varios_elementos_controi_filtro(tabela, filtro,
                                                           colunas, conn)
    ids_variacoes_db = [prod["id_produto_filho"] for prod in variacoes_db]
    ids_variacoes_api = [prod["id"] for prod in variacoes_api]

    ids_variacoes = list(set(ids_variacoes_db) - set(ids_variacoes_api))

    for id_variacao in ids_variacoes:
        variacao_modificada = _solicita_manipula_variacao_excluida(id_produto,
                                                                   id_variacao,
                                                                   conn)
        if variacao_modificada:
            db_atualizar_uma_linha("produtos",
                                   list(variacao_modificada.keys()),
                                   variacao_modificada, "id_bling",
                                   id_variacao, conn)

    return


def _solicita_manipula_variacao_excluida(id_pai, id_produto, conn):
    produto = API.solicita_na_api("/produtos/"+str(id_produto))['data']

    log.info("Manipula dados do produto")
    valores_produto_api = _modifica_valores_produto(produto, conn, id_pai)
    valores_produto_api.pop("criado_em")

    return item_com_valores_atualizados(valores_produto_api, "produtos",
                                        "id_bling", conn)


def _solicita_variacao_para_atualizar(produto_variacao, variacao, conn):
    """Solicita produto e retorna dict pronto para inserir."""
    variacao.pop("criado_em")
    variacao_modificado = item_com_valores_atualizados(variacao, "produtos",
                                                       "id_bling", conn)

    produto_variacao_modificado = item_com_valores_atualizados(
        produto_variacao, "produto_variacao", "id_produto_filho", conn)

    return produto_variacao_modificado, variacao_modificado


def _atualiza_variacao(produto_variacao, variacao, conn):
    """Atualiza uma variação que já existe."""
    colunas_prod = TABELAS_COLUNAS["produtos"][:]
    colunas_prod.remove("criado_em")
    colunas_prod_var = TABELAS_COLUNAS["produto_variacao"][:]
    colunas_prod_var.remove("id")

    if variacao:
        log.info(f"Atualiza variacao do produto {variacao['id_bling']}")
        # Atualiza na tabela de produtos
        db_atualizar_uma_linha("produtos", colunas_prod, variacao, "id_bling",
                               valor_filtro=variacao["id_bling"], conn=conn)
        # Atualiza estoque
        atualizar_estoque_fornecedor(variacao["id_bling"], conn)

    if produto_variacao:
        # Atualiza na tabela produto_variacao
        db_atualizar_uma_linha("produto_variacao", colunas_prod_var,
                               produto_variacao, "id_produto_filho",
                               valor_filtro=variacao["id_bling"], conn=conn)


def _cria_variacao(produto_variacao, variacao, conn):
    """Insere uma nova variação."""
    log.info(f"Cria nova variacao, Produto {variacao['id_bling']}")

    colunas_prod = TABELAS_COLUNAS["produtos"][:]
    colunas_prod_var = TABELAS_COLUNAS["produto_variacao"][:]
    colunas_prod_var.remove("id")

    # Insere produto
    db_inserir_uma_linha("produtos", colunas_prod, variacao, conn)

    # Insere produto_variacao  # Outra tabela
    db_inserir_uma_linha("produto_variacao", colunas_prod_var, conn=conn,
                         valores=produto_variacao)

    produto_insere_saldo_estoque(variacao["id_bling"], conn)


def atualiza_estoque(saldo_estoque, conn):
    """Manipula o dict de estoque e atuliza no bando de dados."""
    colunas_prod_est = TABELAS_COLUNAS["produtos_estoques"][:]
    colunas_prod_est.remove("id")

    saldos_produto = _modifica_produto_estoque(saldo_estoque)

    _verifica_atualiza_valor_unico(saldos_produto, "produtos_estoques",
                                   colunas=colunas_prod_est,
                                   coluna_busca=["id_produto", "id_deposito"],
                                   conn=conn)


def solicita_produtos_com_midias_vencidas(conn):
    """Solicita os ids dos produtos com mídias vencidas."""
    colunas_retorno = ["id_bling"]

    query = "AS pm"
    query += " JOIN produtos_midias_relacao AS pmr ON pmr.id_image = pm.id"
    query += " JOIN produtos AS p ON p.id_bling = pmr.id_produto"
    query += " WHERE validade < CURRENT_TIMESTAMP"

    produtos_com_midias_desatualizadas = (
        db_pega_varios_elementos_controi_filtro("produtos_midias",
                                                query,
                                                colunas_retorno, conn))
    ids_produtos = [item["id_bling"] for item
                    in produtos_com_midias_desatualizadas]
    ids_produtos = list(set(ids_produtos))
    ids_produtos.sort()

    return ids_produtos


def solicita_midias_produtos(conn, id_produto):
    """Retorna todas ids das mídias do produto."""
    colunas_retorno = ["id_image"]

    query = "AS pmr"
    query += " JOIN produtos AS p ON p.id_bling = pmr.id_produto"
    query += f" WHERE p.id_bling={id_produto}"

    ids_midias_desatualizadas = (
        db_pega_varios_elementos_controi_filtro("produtos_midias_relacao",
                                                query,
                                                colunas_retorno, conn))
    ids_midias = [item["id_image"] for item
                  in ids_midias_desatualizadas]
    ids_midias = list(set(ids_midias))
    ids_midias.sort()

    return ids_midias


def manipula_midias_atualizadas(conn, imagens):
    """Cria dict das imagens adequadas para o banco de dados."""
    formato_data = "%Y-%m-%d %H:%M:%S"

    midias_atualizadas = []
    for origem in list(imagens.keys()):  # Externa ou interna
        for obj_imagem in imagens[origem]:  # dict da imagem
            imagem = {
                "tipo": True, "url": obj_imagem["link"],
                "url_miniatura": obj_imagem["linkMiniatura"],
                "validade": datetime.strptime(obj_imagem["validade"],
                                              formato_data).astimezone(FUSO)
                }
            midias_atualizadas.append(imagem)

    return midias_atualizadas


def cria_atualiza_midia_produtos(conn, imagens_api, midias_db, id_produto):
    """Atualiza as midias e adiciona novas mídias adicionadas."""
    tabela = "produtos_midias"
    colunas = TABELAS_COLUNAS[tabela][:]
    colunas.remove("criado_em")
    colunas.remove("id")

    # Atualiza imagens
    for id_midias_db in midias_db:
        db_atualizar_uma_linha(tabela, colunas, imagens_api.pop(0),
                               ["id"], id_midias_db, conn)

    # Insere imagens novas do produto
    for dict_imagem in imagens_api:
        id_foto = db_inserir_uma_linha(tabela, colunas,
                                       dict_imagem, conn)["id"]

        midia_relacao = {"id_produto": id_produto,
                         "id_image": id_foto}
        db_inserir_uma_linha("produtos_midias_relacao",
                             ["id_produto", "id_image"],
                             midia_relacao, conn)

    return


def atualiza_midia_produtos(conn, imagens_api, midias_db, id_produto):
    """Atualiza midias dos produtosno banco de dados."""
    tabela = "produtos_midias"
    colunas = TABELAS_COLUNAS[tabela][:]
    colunas.remove("criado_em")
    colunas.remove("id")

    id_midia_principal = midias_db[0]

    # Atualiza imagens
    for dict_imagem in imagens_api:
        db_atualizar_uma_linha(tabela, colunas, dict_imagem,
                               ["id"], midias_db.pop(0), conn)

    agora = datetime.now(FUSO)
    db_atualizar_uma_linha("produtos", ["id_midia_principal", "alterado_em"],
                           {"id_midia_principal": id_midia_principal,
                            "alterado_em": agora},
                           "id_bling", id_produto, conn)
    # Excluir imagens que sobraram e estão vencidas.
    if midias_db:
        db_deletar_varias_linhas(tabela, "id", midias_db, conn)


if __name__ == "__main__":
    pass
