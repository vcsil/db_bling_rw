#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 17:29:39 2023.

@author: vcsil
"""
from preencherModulos.utils import (formata_data, verifica_preenche_valor,
                                    db_pega_um_elemento, db_inserir_uma_linha,
                                    db_inserir_varias_linhas,
                                    api_pega_todos_id)

from datetime import datetime
import logging

log = logging.getLogger(__name__)

"""Funções utéis para preencher produtos."""


def solicita_categeoria(rota: str, api):
    """Solicita a categoria e retorna os dados e a relação pai/filho."""
    categoria = api.solicita_na_api(rota)['data']
    valores_categoria = _modifica_valores_categoria(categoria)

    log.info("Manipula dados da categoria")
    categoria_pai = categoria["categoriaPai"]["id"]

    if categoria_pai:
        relacao = {"id_categoria_pai": categoria_pai,
                   "id_categoria_filho": categoria["id"]}
        return (relacao, valores_categoria)
    else:
        return (False, valores_categoria)


def _modifica_valores_categoria(categoria: dict):
    valores_categoria = {
        "id_bling": categoria["id"],
        "nome": categoria["descricao"]
    }
    return valores_categoria


def solicita_deposito(rota: str, api):
    """Solicita o deposito na API."""
    deposito = api.solicita_na_api(rota)['data']
    log.info("Manipula dados do deposito")
    valores_deposito = _modifica_valores_deposito(deposito)

    return valores_deposito


def _modifica_valores_deposito(deposito: dict):
    valores_deposito = {
        "id_bling": deposito["id"],
        "descricao": deposito["descricao"],
        "situacao": bool(deposito['situacao']),
        "padrao": deposito['padrao'],
        "desconsiderar_saldo": deposito['desconsiderarSaldo'],
    }
    return valores_deposito


def solicita_ids_produtos(api) -> list:
    """Solicita e retorna o ID de todos os produtos (excluidos inclusos)."""
    # Pega todos produtos
    ids_produtos = api_pega_todos_id(api, '/produtos?criterio=5&tipo=T&')
    # Pega produtos excluidos
    ids_produtos += api_pega_todos_id(api, '/produtos?criterio=4&tipo=T&')
    ids_produtos.sort()
    # Pega variações de produtos
    ids_variacoes = api_pega_todos_id(api, '/produtos?criterio=5&tipo=V&')
    ids_variacoes.sort()

    # Remover as ids das variações
    ids_produtos = list(set(ids_produtos) - set(ids_variacoes))
    return ids_produtos


def solicita_produto(idProduto: int, tabelas_colunas: dict,
                     api, db, conn, fuso, inserir_produto: bool = False):
    """Solicita o produto na API e pode inserir no banco de dados."""
    produto = api.solicita_na_api("/produtos/"+str(idProduto))['data']

    # Se o produto for uma variação
    if ("variacao" in produto.keys()):
        return (produto, False)

    log.info("Manipula dados do produto")
    valores_produto = _modifica_valores_produto(produto=produto, db=db,
                                                conn=conn, fuso=fuso)

    # Se o produto tiver variações, vai enviar o dict das variações separado.
    if len(produto["variacoes"]) > 0:
        variacoes = produto["variacoes"]  # List de dicts com o formato do pai

        if inserir_produto:
            _insere_produto(produto=valores_produto, db=db, conn=conn,
                            colunas=tabelas_colunas['produtos'][:])

        return (variacoes, valores_produto)
    else:
        if inserir_produto:
            _insere_produto(produto=valores_produto, db=db, conn=conn,
                            colunas=tabelas_colunas['produtos'][:])
        return (False, valores_produto)


def _modifica_valores_produto(produto: dict, db, conn, fuso, id_pai=None):
    valores_produto = {
        "id_bling": produto["id"],
        "nome": produto["nome"],
        "codigo": produto["codigo"],
        "preco": int(produto["preco"]*100),
        "id_tipo_produto": db_pega_um_elemento(
            tabela_busca="produtos_tipos", coluna_busca='sigla',
            valor_busca=produto["tipo"], colunas_retorno=["id"],
            db=db, conn=conn)["id"],
        "situacao_produto": _formata_situacao_produto(produto["situacao"]),
        "id_formato_produto": db_pega_um_elemento(
            tabela_busca="produtos_formatos", coluna_busca='sigla',
            valor_busca=produto["formato"], colunas_retorno=["id"],
            db=db, conn=conn)["id"],
        "id_produto_pai": id_pai,
        "descricao_curta": produto["descricaoCurta"],
        "data_validade": formata_data(produto["dataValidade"]),
        "unidade": produto["unidade"],
        "peso_liquido": int(produto["pesoLiquido"]*100),
        "peso_bruto": int(produto["pesoBruto"]*100),
        "volumes": produto["volumes"],
        "itens_por_caixa": produto["itensPorCaixa"],
        "gtin": produto["gtin"],
        "gtin_embalagem": produto["gtinEmbalagem"],
        "id_tipo_producao": db_pega_um_elemento(
            tabela_busca="produtos_tipo_producao", coluna_busca='sigla',
            valor_busca=produto["tipoProducao"], colunas_retorno=["id"],
            db=db, conn=conn)["id"],
        "id_condicao_producao": produto["condicao"],
        "frete_gratis": produto["freteGratis"],
        "marca": produto["marca"] if produto["marca"] else "Marca",
        "descricao_complementar": produto["descricaoComplementar"],
        "link_externo": produto["linkExterno"],
        "observacoes": produto["observacoes"],
        "id_categoria_produto": produto["categoria"]["id"],
        "estoque_minimo": produto["estoque"]["minimo"],
        "estoque_maximo": produto["estoque"]["maximo"],
        "estoque_crossdocking": produto["estoque"]["crossdocking"],
        "estoque_localizacao": produto["estoque"]["localizacao"],
        "id_dimensoes": _formata_dimensoes(dimensoes_api=produto["dimensoes"],
                                           db=db, conn=conn),
        "ncm": produto["tributacao"]["ncm"],
        "cest": produto["tributacao"]["cest"],
        "id_midia_principal": _formata_midia(
            url_midia=produto["midia"]["imagens"]["externas"],
            db=db, conn=conn),
        "criado_em": datetime.now(fuso)
    }
    for chave, valor in valores_produto.items():
        if (valor == ''):
            valores_produto[chave] = None

    return valores_produto


def _formata_situacao_produto(situacao):
    """'Ativo': True, 'Inativo': False."""
    if (situacao == "A"):
        return "Ativo"
    elif (situacao == "I"):
        return "Inativo"
    elif (situacao == "E"):
        return "Excluido"


def _formata_dimensoes(dimensoes_api, db, conn):
    for key in dimensoes_api.keys():
        if key != "unidadeMedida":
            dimensoes_api[key] = int(dimensoes_api[key] * 100)
    colunas = list(dimensoes_api.keys())
    colunas[colunas.index("unidadeMedida")] = "unidade_medida"
    valores = list(dimensoes_api.values())

    id_dimensao = verifica_preenche_valor(
        tabela_busca="dimensoes", coluna_busca=colunas, valor_busca=valores,
        list_colunas=['id']+colunas, db=db, conn=conn)

    return id_dimensao


def _formata_midia(url_midia, db, conn):
    coluna = "url"

    if len(url_midia) > 0:
        valor = url_midia[0]

        id_midia = verifica_preenche_valor(
            tabela_busca="produtos_midias", coluna_busca=coluna, db=db,
            valor_busca=valor, list_colunas=["id", "tipo", "url"], conn=conn)
        return id_midia
    else:
        return None


def _insere_produto(produto: dict, colunas: list, db, conn):
    """Insere o produto manipulado no banco de dados."""
    log.info(f"Insere produto {produto['id_bling']} no banco de dados")
    db_inserir_uma_linha(tabela="produtos", valores=produto, db=db, conn=conn,
                         colunas=colunas)


def solicita_insere_variacao(
        dict_variacao: dict,
        tabelas_colunas: dict,
        id_Pai: int,
        fuso, db, conn):
    """Solicita produto variação na API, trata e insere no banco de dados."""
    log.info(f"Insere variacao {dict_variacao['id']}")
    colunas_produtos = tabelas_colunas["produtos"][:]

    colunas_produto_variacao = tabelas_colunas["produto_variacao"][:]
    colunas_produto_variacao.remove('id')

    produto_variacao, produto = _solicita_variacao(variacao=dict_variacao,
                                                   db=db, fuso=fuso, conn=conn,
                                                   id_pai=id_Pai)

    log.info(f"Insere produto {dict_variacao['id']} no banco de dados")
    db_inserir_uma_linha(tabela="produtos", colunas=colunas_produtos,
                         valores=produto, db=db, conn=conn)

    log.info("Insere produto_variacao")  # Outra tabela
    db_inserir_uma_linha(tabela="produto_variacao", valores=produto_variacao,
                         colunas=colunas_produto_variacao, db=db, conn=conn)


def _solicita_variacao(variacao: dict, id_pai: int, fuso, db, conn):
    """Monta objeto variacao."""
    valores_produto = _modifica_valores_produto(
        produto=variacao, db=db, conn=conn, fuso=fuso, id_pai=id_pai)

    produto_variacao = _modifica_produto_variacao(variacao, id_pai)
    return (produto_variacao, valores_produto)


def _modifica_produto_variacao(produto, id_pai):
    produto_variacao = {
        "id_produto_pai": id_pai,
        "id_produto_filho": produto['id'],
        "nome": produto["variacao"]["nome"],
        "ordem": produto["variacao"]["ordem"],
        "clone_pai": produto["variacao"]["produtoPai"]["cloneInfo"]
    }
    return produto_variacao


def produto_insere_saldo_estoque(
        tabelas_colunas: dict,
        id_produto: int,
        api, db, conn):
    """Pega saldos da API e salva no banco de dados."""
    log.info("Insere saldos de estoque e fornecedor")

    colunas_produto_estoques = tabelas_colunas["produtos_estoques"][:]
    colunas_produto_estoques.remove('id')

    colunas_produto_forncdr = tabelas_colunas["produto_fornecedor"][:]

    produto_fornecedor, produtos_estoques = (
        _solicita_estoque_fornecedor(id_produto=id_produto, api=api))

    db_inserir_varias_linhas(tabela="produtos_estoques", db=db, conn=conn,
                             colunas=colunas_produto_estoques,
                             valores=produtos_estoques)
    db_inserir_varias_linhas(tabela="produto_fornecedor", db=db, conn=conn,
                             colunas=colunas_produto_forncdr,
                             valores=produto_fornecedor)


def _solicita_estoque_fornecedor(id_produto: int, api):
    """Solicita saldo e estoque na api."""
    rota1 = "/estoques/saldos?idsProdutos[]=" + str(id_produto)
    produto_estoque = api.solicita_na_api(rota1)['data'][0]

    log.info("Manipula dados dos produtos_estoques")
    saldo_produto = _modifica_produto_estoque(saldos=produto_estoque)

    rota2 = "/produtos/fornecedores?idProduto=" + str(id_produto)
    produto_fornecedor = api.solicita_na_api(rota2)['data']

    log.info("Manipula dados dos produto_fornecedor")
    fornecedor_produto = _modifica_produto_fornecedor(
        fornecedor=produto_fornecedor)

    return (fornecedor_produto, saldo_produto)


def _modifica_produto_estoque(saldos: dict):
    list_produto_estoque = []
    for idx in range(len(saldos["depositos"])):
        produto_estoque = {
            "id_produto": saldos["produto"]["id"],
            "id_deposito": saldos["depositos"][idx]["id"],
            "saldo_fisico": saldos["depositos"][idx]["saldoFisico"],
            "saldo_virtual": saldos["depositos"][idx]["saldoVirtual"]
        }
        list_produto_estoque.append(produto_estoque)
    return list_produto_estoque


def _modifica_produto_fornecedor(fornecedor: dict):
    list_produto_fornecedor = []
    for idx in range(len(fornecedor)):
        id_fornecedor = fornecedor[idx]["fornecedor"]["id"]
        id_fornecedor = id_fornecedor if id_fornecedor != 0 else None
        produto_fornecedor = {
            "id_bling": fornecedor[idx]["id"],
            "descricao": fornecedor[idx]["descricao"],
            "codigo": fornecedor[idx]["codigo"],
            "preco_custo": int(fornecedor[idx]["precoCusto"]*100),
            "preco_compra": int(fornecedor[idx]["precoCompra"]*100),
            "padrao": fornecedor[idx]["padrao"],
            "id_produto": fornecedor[idx]["produto"]["id"],
            "id_fornecedor": id_fornecedor
        }
        list_produto_fornecedor.append(produto_fornecedor)
    return list_produto_fornecedor


def insere_segunda_tentativa(tabelas_colunas: dict, produto: int,
                             fuso, api, db, conn):
    """Trata produtos não inseridos de primeiros."""
    # Tira a variação do nome do produto
    nome_produto = " ".join([nome for nome in produto["nome"]
                             .split() if ":" not in nome])
    rota = f"/produtos?pagina=1&limite=1&tipo=C&nome={nome_produto}"
    produto_pai = api.solicita_na_api(rota)["data"]
    if not produto_pai:
        rota = "/produtos?pagina=1&limite=1&tipo=PS&nome=Generico"
        produto_pai = api.solicita_na_api(rota)["data"]
    id_Pai = produto_pai[0]["id"]

    solicita_insere_variacao(
        dict_variacao=produto, fuso=fuso, id_Pai=id_Pai,
        tabelas_colunas=tabelas_colunas, db=db, conn=conn)


if __name__ == "__main__":
    pass
