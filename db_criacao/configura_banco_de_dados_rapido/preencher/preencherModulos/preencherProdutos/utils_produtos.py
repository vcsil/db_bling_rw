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
from config.constants import API, FUSO, TABELAS_COLUNAS, IMAGE_DIR

from datetime import datetime
from tqdm import tqdm
import requests
import logging
import os

log = logging.getLogger("root")

"""Funções utéis para preencher produtos."""


def solicita_categeoria(rota: str):
    """Solicita a categoria e retorna os dados e a relação pai/filho."""
    categoria = API.solicita_na_api(rota)["data"]
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


def solicita_deposito(rota: str):
    """Solicita o deposito na API."""
    deposito = API.solicita_na_api(rota)["data"]
    log.info("Manipula dados do deposito")
    valores_deposito = _modifica_valores_deposito(deposito)

    return valores_deposito


def _modifica_valores_deposito(deposito: dict):
    valores_deposito = {
        "id_bling": deposito["id"],
        "descricao": deposito["descricao"],
        "situacao": bool(deposito["situacao"]),
        "padrao": deposito["padrao"],
        "desconsiderar_saldo": deposito["desconsiderarSaldo"],
    }
    return valores_deposito


def solicita_ids_produtos() -> list:
    """Solicita e retorna o ID de todos os produtos (excluidos inclusos)."""
    # Pega todos produtos
    ids_todos_produtos = api_pega_todos_id("/produtos?criterio=5&tipo=T&")
    # Pega variações de produtos
    ids_variacoes = api_pega_todos_id("/produtos?criterio=5&tipo=V&")
    # Pega excluidos
    ids_excluidos = api_pega_todos_id("/produtos?criterio=4&tipo=T&")

    # Remover as ids das variações
    ids_produtos = list(set(ids_todos_produtos) - set(ids_variacoes))
    # Adiciona excluidos
    ids_produtos = list(set(ids_produtos + ids_excluidos))
    ids_produtos.sort()

    return ids_produtos


def solicita_produto(idProduto: int, conn, inserir_produto: bool = False):
    """Solicita o produto na API e pode inserir no banco de dados."""
    produto = API.solicita_na_api("/produtos/"+str(idProduto))["data"]

    # Se o produto for uma variação
    if ("variacao" in produto.keys()):
        return (produto, False)

    log.info("Manipula dados do produto")
    valores_produto = _modifica_valores_produto(produto, conn,
                                                inserir_produto=inserir_produto)

    # Se o produto tiver variações, vai enviar o dict das variações separado.
    if len(produto["variacoes"]) > 0:
        variacoes = produto["variacoes"]  # List de dicts com o formato do pai

        if inserir_produto:
            _insere_produto(valores_produto, TABELAS_COLUNAS["produtos"][:],
                            conn)

        return (variacoes, valores_produto)
    else:
        if inserir_produto:
            _insere_produto(valores_produto, TABELAS_COLUNAS["produtos"][:],
                            conn)
        return (False, valores_produto)


def _modifica_valores_produto(produto: dict, conn, id_pai: bool = None,
                              inserir_produto: bool = False):
    id_tipo_producao = _pega_tipo_producao(produto, conn)

    valores_produto = {
        "id_bling": produto["id"],
        "nome": produto["nome"],
        "codigo": produto["codigo"],
        "preco": round(produto["preco"]*100),
        "id_tipo_produto": db_pega_um_elemento("produtos_tipos", "sigla",
                                               produto["tipo"], ["id"],
                                               conn)["id"],
        "situacao_produto": _formata_situacao_produto(produto["situacao"]),
        "id_formato_produto": db_pega_um_elemento("produtos_formatos", "sigla",
                                                  produto["formato"], ["id"],
                                                  conn)["id"],
        "id_produto_pai": id_pai,
        "descricao_curta": produto["descricaoCurta"],
        "data_validade": formata_data(produto["dataValidade"]),
        "unidade": produto["unidade"],
        "peso_liquido": round(produto["pesoLiquido"]*100),
        "peso_bruto": round(produto["pesoBruto"]*100),
        "volumes": produto["volumes"],
        "itens_por_caixa": produto["itensPorCaixa"],
        "gtin": produto["gtin"],
        "gtin_embalagem": produto["gtinEmbalagem"],
        "id_tipo_producao": id_tipo_producao,
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
        "id_dimensoes": _formata_dimensoes(produto["dimensoes"], conn),
        "ncm": produto["tributacao"]["ncm"],
        "cest": produto["tributacao"]["cest"],
        "id_midia_principal": _formata_midia(produto["midia"], produto["id"],
                                             inserir_produto, conn),
        "criado_em": datetime.now(FUSO),
        "alterado_em": None
    }
    for chave, valor in valores_produto.items():
        if (valor == ""):
            valores_produto[chave] = None

    return valores_produto


def _pega_tipo_producao(produto, conn):
    if "tipoProducao" in list(produto.keys()):
        return db_pega_um_elemento("produtos_tipo_producao", "sigla",
                                   produto["tipoProducao"], ["id"], conn)["id"]
    else:
        return None


def _formata_situacao_produto(situacao):
    """'Ativo': True, 'Inativo': False."""
    if (situacao == "A"):
        return "Ativo"
    elif (situacao == "I"):
        return "Inativo"
    elif (situacao == "E"):
        return "Excluido"


def _formata_dimensoes(dimensoes_api, conn):
    for key in dimensoes_api.keys():
        if key != "unidadeMedida":
            dimensoes_api[key] = round(dimensoes_api[key] * 100)
    colunas = list(dimensoes_api.keys())
    colunas[colunas.index("unidadeMedida")] = "unidade_medida"
    valores = list(dimensoes_api.values())

    id_dimensao = verifica_preenche_valor("dimensoes", colunas, valores,
                                          ["id"]+colunas, conn)

    return id_dimensao


def _formata_midia(midias, id_produto, inserir_produto, conn):
    # Produto que não é para inserir já existe no banco de dados
    if not (inserir_produto):
        midia = db_pega_um_elemento("produtos", ["id_bling"], [id_produto],
                                    ["id_midia_principal"], conn)

        return midia["id_midia_principal"] if midia else midia

    _formata_midia_video(conn, midias["video"])

    midia_principal = _formata_midia_imagem(conn, midias["imagens"],
                                            id_produto)

    return midia_principal if midia_principal else None


def _formata_midia_video(conn, video):
    colunas = ["tipo", "url", "url_miniatura", "validade"]

    if video["url"] != "":
        video = {"tipo": False, "url": video["url"], "url_miniatura": None,
                 "validade": datetime.now(FUSO)}
        db_inserir_uma_linha("produtos_midias", colunas, [video], conn)


def _formata_midia_imagem(conn, imagens, id_produto):
    colunas = ["tipo", "url", "url_miniatura", "validade", "diretorio_local"]
    formato_data = "%Y-%m-%d %H:%M:%S"

    midia_principal = False
    for origem in list(imagens.keys()):  # Externa ou interna
        for obj_imagem in imagens[origem]:  # dict da imagem
            path = download_localmente(imagens[origem].index(obj_imagem),
                                       id_produto, obj_imagem["link"])

            imagem = {
                "tipo": True, "url": obj_imagem["link"],
                "url_miniatura": obj_imagem["linkMiniatura"],
                "validade": datetime.strptime(obj_imagem["validade"],
                                              formato_data).astimezone(FUSO),
                "diretorio_local": path
                }
            id_foto = db_inserir_uma_linha("produtos_midias", colunas, imagem,
                                           conn)["id"]

            midia_relacao = {"id_produto": id_produto, "id_image": id_foto}
            db_inserir_uma_linha("produtos_midias_relacao",
                                 ["id_produto", "id_image"], midia_relacao,
                                 conn)
            if not (midia_principal):
                midia_principal = id_foto

    return midia_principal


def download_localmente(id_foto, id_produto, image_url):
    """Gerencia o download da imagem."""
    # Diretorio local para salvar as imagens
    local_directory = f"{IMAGE_DIR}{id_produto}"

    # Verifica se o diretório já existe.
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    file_name = os.path.basename(str(id_foto)+".jpeg")
    local_path = os.path.join(local_directory, file_name)
    print(f"\nBaixando {id_foto} para {local_path}")
    download_image(image_url, local_path)
    return local_path.split("..")[-1]


def download_image(url, local_path):
    """Responsável por fazer o download da imagem."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    t = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(local_path, 'wb') as file:
        for data in response.iter_content(block_size):
            t.update(len(data))
            file.write(data)
    t.close()


def _insere_produto(produto: dict, colunas: list, conn):
    """Insere o produto manipulado no banco de dados."""
    log.info(f"Insere produto {produto['id_bling']} no banco de dados")
    db_inserir_uma_linha("produtos", colunas, produto, conn)


def solicita_insere_variacao(
        dict_variacao: dict,
        id_Pai: int,
        conn):
    """Solicita produto variação na API, trata e insere no banco de dados."""
    log.info(f"Insere variacao {dict_variacao['id']}")
    colunas_produtos = TABELAS_COLUNAS["produtos"][:]

    colunas_produto_variacao = TABELAS_COLUNAS["produto_variacao"][:]
    colunas_produto_variacao.remove("id")

    produto_variacao, produto = _solicita_variacao(dict_variacao, id_Pai, conn,
                                                   True)

    log.info(f"Insere produto {dict_variacao['id']} no banco de dados")
    db_inserir_uma_linha("produtos", colunas_produtos, produto, conn)

    log.info("Insere produto_variacao")  # Outra tabela
    db_inserir_uma_linha("produto_variacao", colunas_produto_variacao,
                         produto_variacao, conn)


def _solicita_variacao(variacao: dict, id_pai: int, conn,
                       inserir_produto: bool = False):
    """Monta objeto variacao."""
    valores_produto = _modifica_valores_produto(variacao, conn, id_pai,
                                                inserir_produto)

    produto_variacao = _modifica_produto_variacao(variacao, id_pai)
    return (produto_variacao, valores_produto)


def _modifica_produto_variacao(produto, id_pai):
    produto_variacao = {
        "id_produto_pai": id_pai,
        "id_produto_filho": produto["id"],
        "nome": produto["variacao"]["nome"],
        "ordem": produto["variacao"]["ordem"],
        "clone_pai": produto["variacao"]["produtoPai"]["cloneInfo"]
    }
    return produto_variacao


def produto_insere_saldo_estoque(id_produto: int, conn):
    """Pega saldos da API e salva no banco de dados."""
    log.info("Insere saldos de estoque e fornecedor")

    colunas_produto_estoques = TABELAS_COLUNAS["produtos_estoques"][:]
    colunas_produto_estoques.remove("id")

    colunas_produto_forncdr = TABELAS_COLUNAS["produto_fornecedor"][:]

    produto_fornecedor, produtos_estoques = (
        _solicita_estoque_fornecedor(id_produto))

    db_inserir_varias_linhas("produtos_estoques", colunas_produto_estoques,
                             produtos_estoques, conn)
    db_inserir_varias_linhas("produto_fornecedor", colunas_produto_forncdr,
                             produto_fornecedor, conn)


def _solicita_estoque_fornecedor(id_produto: int):
    """Solicita saldo e estoque na api."""
    rota1 = "/estoques/saldos?idsProdutos[]=" + str(id_produto)
    produto_estoque = API.solicita_na_api(rota1)["data"][0]

    log.info("Manipula dados dos produtos_estoques")
    saldo_produto = _modifica_produto_estoque(saldos=produto_estoque)

    rota2 = "/produtos/fornecedores?idProduto=" + str(id_produto)
    produto_fornecedor = API.solicita_na_api(rota2)["data"]

    log.info("Manipula dados dos produto_fornecedor")
    fornecedor_produto = _modifica_produto_fornecedor(produto_fornecedor)

    return (fornecedor_produto, saldo_produto)


def _modifica_produto_estoque(saldos: dict):
    list_produto_estoque = []
    for idx in range(len(saldos["depositos"])):
        produto_estoque = {
            "id_produto": saldos["produto"]["id"],
            "id_deposito": saldos["depositos"][idx]["id"],
            "saldo_fisico": saldos["depositos"][idx]["saldoFisico"],
            "saldo_virtual": saldos["depositos"][idx]["saldoVirtual"],
            "alterado_em": None
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
            "preco_custo": round(fornecedor[idx]["precoCusto"]*100),
            "preco_compra": round(fornecedor[idx]["precoCompra"]*100),
            "padrao": fornecedor[idx]["padrao"],
            "id_produto": fornecedor[idx]["produto"]["id"],
            "id_fornecedor": id_fornecedor
        }
        list_produto_fornecedor.append(produto_fornecedor)
    return list_produto_fornecedor


def insere_segunda_tentativa(produto: int, conn):
    """Trata produtos não inseridos de primeiros."""
    # Tira a variação do nome do produto
    nome_produto = " ".join([nome for nome in produto["nome"]
                             .split() if ":" not in nome])
    rota = f"/produtos?pagina=1&limite=1&tipo=C&nome={nome_produto}"
    produto_pai = API.solicita_na_api(rota)["data"]
    if not produto_pai:
        rota = "/produtos?pagina=1&limite=1&tipo=PS&nome=Generico"
        produto_pai = API.solicita_na_api(rota)["data"]
    id_Pai = produto_pai[0]["id"]

    solicita_insere_variacao(produto, id_Pai, conn)


if __name__ == "__main__":
    pass
