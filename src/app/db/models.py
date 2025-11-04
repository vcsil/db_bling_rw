#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 13 22:28:49 2025.

@author: vcsil
"""
from __future__ import annotations

from sqlalchemy import (
    Integer, BigInteger, SmallInteger, String, Text, Boolean, Date, DateTime,
    ForeignKey, CheckConstraint, UniqueConstraint, Identity, CHAR, text
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from typing import Optional
from datetime import date, datetime


class Base(DeclarativeBase):
    """Classe-base declarativa, usada por todas as entidades."""

    pass


# ===============================
# ============CONTATOS===========
# ===============================

class ContatosSituacao(Base):  # 1
    """Situação do contato."""

    __tablename__ = "contatos_situacao"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
        CheckConstraint("sigla <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(String(20), nullable=False, unique=True,
                                      comment=("Situação do contato\n"
                                               "`A` Ativo\n"
                                               "`E` Excluído\n"
                                               "`I` Inativo\n"
                                               "`S` Sem movimentação"))
    sigla: Mapped[str] = mapped_column(CHAR(1), nullable=False, unique=True)


class ContatosTipo(Base):  # 2
    """Tipo de contato. PJ, PF,Ex."""

    __tablename__ = "contatos_tipo"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
        CheckConstraint("sigla <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(String(20), nullable=False, unique=True,
                                      comment=("Tipo da pessoa"
                                               "`J` Jurídica"
                                               "`F` Física"
                                               "`E` Estrangeira"))
    sigla: Mapped[str] = mapped_column(CHAR(1), nullable=False, unique=True)


class ContatosIndicadorInscricaoEstadual(Base):  # 3
    """Indicador de inscrição estadual."""

    __tablename__ = "contatos_indicador_inscricao_estadual"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    nome: Mapped[str] = mapped_column(
        String(63), nullable=False, unique=True,
        comment=(
            "Indicador de inscrição estadual"
            "`1` Contribuinte ICMS "
            "`2` Contribuinte isento de Inscrição no cadastro de Contribuintes"
            "`9` Não Contribuinte"))


class ContatosClassificacao(Base):  # 4
    """Classificação dos contatos. (Vendedor, Fornecedor, etc."""

    __tablename__ = "contatos_classificacao"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    nome: Mapped[str] = mapped_column(String(63), nullable=False, unique=True,
                                      comment='Fornecedor, vendedor, etc.')


class EnderecoPaises(Base):  # 5
    """Paises do endereço."""

    __tablename__ = "endereco_paises"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
        {'comment': 'Bloqueio para repetir país'},
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(String(63), nullable=False, unique=True)


class EnderecoUnidadeFederativa(Base):  # 6
    """Unidades Federativas dos Endereços."""

    __tablename__ = "endereco_unidade_federativa"

    __table_args__ = (
        UniqueConstraint("nome", "id_pais", name="uq_uf_idpais"),
        {'comment': 'Bloqueio para repetir a mesma UF em um mesmo País'},
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[Optional[str]] = mapped_column(String(63))
    id_pais: Mapped[int] = mapped_column(
        Integer, ForeignKey("endereco_paises.id"), nullable=False)

    pais: Mapped["EnderecoPaises"] = relationship(
        "EnderecoPaises", backref="endereco_unidade_federativa")


class EnderecoMunicipios(Base):  # 7
    """Endereço dos municipios para endereço."""

    __tablename__ = "endereco_municipios"

    __table_args__ = (
        UniqueConstraint("nome", "id_uf", name="uq_municipio_iduf"),
        {'comment': 'Bloqueio para repetir o mesmo município em um mesmo UF'},
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[Optional[str]] = mapped_column(String(63))
    id_uf: Mapped[int] = mapped_column(
        Integer, ForeignKey("endereco_unidade_federativa.id"), nullable=False)

    uf: Mapped["EnderecoUnidadeFederativa"] = relationship(
        "EnderecoUnidadeFederativa", backref="endereco_municipios")


class EnderecoBairros(Base):  # 8
    """Bairros para endereço."""

    __tablename__ = "endereco_bairros"
    __table_args__ = (
        UniqueConstraint("nome", "id_municipio", name="uq_bairro_idmunicipio"),
        {'comment': 'Bloqueio para repetir o mesmo bairro em mesmo município'},
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[Optional[str]] = mapped_column(String(63))
    id_municipio: Mapped[int] = mapped_column(
        Integer, ForeignKey("endereco_municipios.id"), nullable=False)

    municipio: Mapped["EnderecoMunicipios"] = relationship(
        "EnderecoMunicipios", backref="endereco_bairros")


class Enderecos(Base):  # 9
    """Endereço completo."""

    __tablename__ = "enderecos"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    endereco: Mapped[Optional[str]] = mapped_column(String(127))
    cep: Mapped[Optional[str]] = mapped_column(String(8))

    id_bairro: Mapped[int] = mapped_column(
        Integer, ForeignKey("endereco_bairros.id"), nullable=False)

    id_municipio: Mapped[int] = mapped_column(
        Integer, ForeignKey("endereco_municipios.id"), nullable=False)

    id_uf: Mapped[int] = mapped_column(
        Integer, ForeignKey("endereco_unidade_federativa.id"), nullable=False)

    id_pais: Mapped[int] = mapped_column(
        Integer, ForeignKey("endereco_paises.id"), nullable=False)

    numero: Mapped[Optional[str]] = mapped_column(String(10))
    complemento: Mapped[Optional[str]] = mapped_column(String(127))

    bairro: Mapped["EnderecoBairros"] = relationship(
        "EnderecoBairros", backref="enderecos")
    municipio: Mapped["EnderecoMunicipios"] = relationship(
        "EnderecoMunicipios", backref="enderecos")
    uf: Mapped["EnderecoUnidadeFederativa"] = relationship(
        "EnderecoUnidadeFederativa", backref="enderecos")
    pais: Mapped["EnderecoPaises"] = relationship(
        "EnderecoPaises", backref="enderecos")


class Contatos(Base):  # 10
    """Contatos."""

    __tablename__ = "contatos"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
        CheckConstraint("sexo IN (1, 2, 3)"),
    )

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    sobrenome: Mapped[str] = mapped_column(String(255), nullable=False)
    codigo: Mapped[Optional[str]] = mapped_column(String(45))

    id_situacao_contato: Mapped[int] = mapped_column(
        Integer, ForeignKey("contatos_situacao.id"), nullable=False)

    numero_documento: Mapped[Optional[str]] = mapped_column(
        String(14), comment='CPF ou CNPJ do contato')
    telefone: Mapped[Optional[str]] = mapped_column(String(15),
                                                    comment='+5511998765432')
    celular: Mapped[Optional[str]] = mapped_column(String(15),
                                                   comment='+5511998765432')
    fantasia: Mapped[Optional[str]] = mapped_column(String(63))

    id_tipo_contato: Mapped[int] = mapped_column(
        Integer, ForeignKey("contatos_tipo.id"), nullable=False)

    id_indicador_inscricao_estadual: Mapped[int] = mapped_column(
        Integer, ForeignKey("contatos_indicador_inscricao_estadual.id"),
        nullable=False)

    inscricao_estadual: Mapped[Optional[str]] = mapped_column(String(13))
    rg: Mapped[Optional[str]] = mapped_column(String(10))
    inscricao_municipal: Mapped[Optional[str]] = mapped_column(String(13))
    orgao_emissor: Mapped[Optional[str]] = mapped_column(String(55))
    email: Mapped[Optional[str]] = mapped_column(String(255))

    data_nascimento: Mapped[Optional[date]] = mapped_column(Date)
    sexo: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="1 Masculino\n2 Feminino\n3 Outro",)

    id_classificacao_contato: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("contatos_classificacao.id_bling"))

    cliente_desde: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=text("current_timestamp"))
    alterado_em: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True))

    situacao_contato: Mapped["ContatosSituacao"] = relationship(
        "ContatosSituacao", backref="contatos")
    tipo_contato: Mapped["ContatosTipo"] = relationship(
        "ContatosTipo", backref="contatos")
    indicador_inscricao_estadual: Mapped[
        "ContatosIndicadorInscricaoEstadual"] = relationship(
        "ContatosIndicadorInscricaoEstadual", backref="contatos")
    classificacao_contato: Mapped["ContatosClassificacao"] = relationship(
        "ContatosClassificacao", backref="contatos")


class ContatosEnderecos(Base):  # 11
    """Contatos."""

    __tablename__ = "contatos_enderecos"

    __table_args__ = (
        {'comment': '`0`: Geral \\n `1`: Cobrança'},
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    id_contato: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contatos.id_bling"), nullable=False)
    id_endereco: Mapped[int] = mapped_column(
        Integer, ForeignKey("enderecos.id"), nullable=False)
    tipo_endereco: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    contato: Mapped["Contatos"] = relationship(
        "Contatos", backref="contatos_enderecos")
    endereco: Mapped["Enderecos"] = relationship(
        "Enderecos", backref="contatos_enderecos")


# ===============================
# ============PRODUTOS===========
# ===============================


class ProdutosTipos(Base):  # 12
    """Deposito que o produto esta."""

    __tablename__ = "produtos_tipos"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
        CheckConstraint("sigla <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(String(20), nullable=False, unique=True,
                                      comment=("Tipo do produto"
                                               "`S` Serviço"
                                               "`P` Produto"
                                               "`N` Serviço 06 21 22"))
    sigla: Mapped[str] = mapped_column(CHAR(1), nullable=False, unique=True)


class ProdutosFormatos(Base):  # 13
    """Formato dos produtos."""

    __tablename__ = "produtos_formatos"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
        CheckConstraint("sigla <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(String(15), nullable=False, unique=True,
                                      comment=("Formato do produto"
                                               "`S` Simples"
                                               "`V` Com variações"
                                               "`E` Com composição"))
    sigla: Mapped[str] = mapped_column(CHAR(1), nullable=False, unique=True)


class ProdutosTipoProducao(Base):  # 14
    """Tipo de produção."""

    __tablename__ = "produtos_tipo_producao"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
        CheckConstraint("sigla <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(String(10), nullable=False, unique=True,
                                      comment=("Tipo da produção"
                                               "`P` Própria"
                                               "`T` Terceiros"))
    sigla: Mapped[str] = mapped_column(CHAR(1), nullable=False, unique=True)


class ProdutosCondicao(Base):  # 15
    """Condicoes dos produtos."""

    __tablename__ = "produtos_condicao"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(String(17), nullable=False,
                                      comment=("Condição do produto"
                                               "`0` Não especificado"
                                               "`1` Novo"
                                               "`2` Usado"))


class ProdutosCategorias(Base):  # 16
    """Categorias dos produtos."""

    __tablename__ = "produtos_categorias"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)

    # relações "de volta", com nomes distintos
    relacoes_como_pai = relationship(
        "ProdutosCategoriasRelacao",
        foreign_keys="[ProdutosCategoriasRelacao.id_categoria_pai]",
        back_populates="categoria_pai",
        cascade="all, delete-orphan",
    )
    relacao_como_filho = relationship(
        "ProdutosCategoriasRelacao",
        foreign_keys="[ProdutosCategoriasRelacao.id_categoria_filho]",
        back_populates="categoria_filho",
        uselist=False,  # seu filho é unique=True -> 1:1 p/ esse lado
    )


class ProdutosCategoriasRelacao(Base):  # 17
    """Relação entre as categorias dos produtos."""

    __tablename__ = "produtos_categorias_relacao"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    id_categoria_pai: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos_categorias.id_bling"), nullable=False)
    id_categoria_filho: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos_categorias.id_bling"), nullable=False,
        unique=True)

    categoria_pai = relationship(
        "ProdutosCategorias",
        foreign_keys=[id_categoria_pai],
        back_populates="relacoes_como_pai",
        primaryjoin=id_categoria_pai == ProdutosCategorias.id_bling,  # opcional, deixa explícito
    )
    categoria_filho = relationship(
        "ProdutosCategorias",
        foreign_keys=[id_categoria_filho],
        back_populates="relacao_como_filho",
        primaryjoin=id_categoria_filho == ProdutosCategorias.id_bling,  # opcional
        uselist=False,
    )


class Dimensoes(Base):  # 18
    """Dimensoes das caixas para envio."""

    __tablename__ = "dimensoes"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    largura: Mapped[int] = mapped_column(Integer, nullable=False)
    altura: Mapped[int] = mapped_column(Integer, nullable=False)
    profundidade: Mapped[int] = mapped_column(Integer, nullable=False)
    unidade_medida: Mapped[int] = mapped_column(Integer, nullable=False,
                                                comment=("`0` Metros"
                                                         "`1` Centímetros"
                                                         "`2` Milímetros"))


class ProdutosMidias(Base):  # 19
    """Mídia dos produtos."""

    __tablename__ = "produtos_midias"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    tipo: Mapped[bool] = mapped_column(Boolean, nullable=False,
                                       comment="True: Foto\nFalse: Video")
    url: Mapped[str] = mapped_column(Text, nullable=False)
    url_miniatura: Mapped[Optional[str]] = mapped_column(Text)
    diretorio_local: Mapped[Optional[str]] = mapped_column(
        Text)
    validade: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                               nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=text("current_timestamp"))


class Produtos(Base):  # 20
    """Produtos."""

    __tablename__ = "produtos"

    __table_args__ = (
        # UniqueConstraint("nome", "codigo", "situacao_produto",
        #                  name="uq_nome_codigo"),
        CheckConstraint("nome <> ''"),
        CheckConstraint("codigo <> ''"),
        CheckConstraint("unidade <> ''"),
        CheckConstraint("marca <> ''"),
        CheckConstraint("ncm <> ''"),
        CheckConstraint("cest <> ''"),
    )

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    codigo: Mapped[str] = mapped_column(String(120), nullable=False)
    preco: Mapped[int] = mapped_column(Integer, nullable=False)

    id_tipo_produto: Mapped[int] = mapped_column(
        Integer, ForeignKey("produtos_tipos.id"), nullable=False,
        server_default=text("2"))

    situacao_produto: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("TRUE"),
        comment=("Ação de estoque ao transformar produto Simples em Variação\n"
                 "`TRUE` `Z` Irá zerar os saldos de estoque\n"
                 "`FALSE` `T` Transfere o estoque do produto pai para a "
                 "primeira variação informada"))

    id_formato_produto: Mapped[int] = mapped_column(
        Integer, ForeignKey("produtos_formatos.id"), nullable=False)

    id_produto_pai: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("produtos.id_bling"))

    descricao_curta: Mapped[Optional[str]] = mapped_column(Text)
    data_validade: Mapped[Optional[date]] = mapped_column(Date)
    unidade: Mapped[Optional[str]] = mapped_column(String(6),
                                                   server_default=('UN'))
    peso_liquido: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1"),
        comment='Peso líquido em KG')
    peso_bruto: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1"),
        comment='Peso bruto em KG')
    volumes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1"),
        comment=("Quantidade total de volumes que o produto precisa ser "
                 "dividido para entrega"))
    itens_por_caixa: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1"),
        comment='Quantidade de itens por caixa/embalagem')
    gtin: Mapped[str] = mapped_column(
        String(14),
        comment=("Código GTIN (GTIN-8, GTIN-12, GTIN-13 ou "
                 "GTIN-14) do produto que está sendo comercializado"))
    gtin_embalagem: Mapped[Optional[str]] = mapped_column(
        String(13),
        comment=("Código GTIN (GTIN-8, GTIN-12 ou GTIN-13) da menor unidade "
                 "comercializada no varejo"))

    id_tipo_producao: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("produtos_tipo_producao.id"),
        server_default=text("1"))

    id_condicao_producao: Mapped[int] = mapped_column(
        Integer, ForeignKey("produtos_condicao.id"), nullable=False)

    frete_gratis: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE"),
        comment='Frete grátis\nValor default: `false`')

    marca: Mapped[str] = mapped_column(String(45), nullable=False,
                                       server_default=('RW'))

    descricao_complementar: Mapped[Optional[str]] = mapped_column(Text)
    link_externo: Mapped[Optional[str]] = mapped_column(Text)
    observacoes: Mapped[Optional[str]] = mapped_column(Text)
    descricao_embalagem_discreta: Mapped[Optional[str]] = mapped_column(
        Text, comment=("Descrição discreta do produto para utilizar na "
                       "declaração de conteúdo."))

    id_categoria_produto: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos_categorias.id_bling"), nullable=False)

    action_estoque: Mapped[bool] = mapped_column(Boolean)
    estoque_minimo: Mapped[int] = mapped_column(Integer, nullable=False,
                                                server_default=text("0"))
    estoque_maximo: Mapped[int] = mapped_column(Integer, nullable=False,
                                                server_default=text("0"))
    estoque_crossdocking: Mapped[int] = mapped_column(Integer, nullable=False,
                                                      server_default=text("0"))
    estoque_localizacao: Mapped[str] = mapped_column(String(45))

    id_dimensoes: Mapped[int] = mapped_column(
        Integer, ForeignKey("dimensoes.id"), nullable=False)

    ncm: Mapped[str] = mapped_column(String(10),
                                     server_default=('7113.20.00'))
    cest: Mapped[str] = mapped_column(String(9),
                                      server_default=('28.058.00'))

    id_midia_principal: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("produtos_midias.id"))

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=text("current_timestamp"))
    alterado_em: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True))

    tipo_produto: Mapped["ProdutosTipos"] = relationship(
        "ProdutosTipos", backref="produtos")
    formato_produto: Mapped["ProdutosFormatos"] = relationship(
        "ProdutosFormatos", backref="produtos")
    produto_pai: Mapped["Produtos"] = relationship(
        "Produtos", backref="produtos")
    tipo_producao: Mapped["ProdutosTipoProducao"] = relationship(
        "ProdutosTipoProducao", backref="produtos")
    condicao_producao: Mapped["ProdutosCondicao"] = relationship(
        "ProdutosCondicao", backref="produtos")
    categoria_produto: Mapped["ProdutosCategorias"] = relationship(
        "ProdutosCategorias", backref="produtos")
    dimensoes: Mapped["Dimensoes"] = relationship(
        "Dimensoes", backref="produtos")
    midia_principal: Mapped["ProdutosMidias"] = relationship(
        "ProdutosMidias", backref="produtos")


class ProdutosDepositos(Base):  # 21
    """Deposito que o produto esta."""

    __tablename__ = "produtos_depositos"

    __table_args__ = (
        CheckConstraint("descricao <> ''"),
    )

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    descricao: Mapped[str] = mapped_column(String(45), nullable=False)
    situacao: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("TRUE"),
        comment=("`0` Inativo"
                 "`1` Ativo"))
    padrao: Mapped[bool] = mapped_column(Boolean, nullable=False,
                                         server_default=text("TRUE"))
    desconsiderar_saldo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE"))


class ProdutosEstoques(Base):  # 22
    """Saldo de produtos por estoque."""

    __tablename__ = "produtos_estoques"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    id_produto: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos.id_bling"), nullable=False)
    id_deposito: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos_depositos.id_bling"), nullable=False)
    saldo_fisico: Mapped[int] = mapped_column(Integer, nullable=False)
    saldo_virtual: Mapped[int] = mapped_column(Integer, nullable=False)
    alterado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("current_timestamp"))

    produto: Mapped["Produtos"] = relationship(
        "Produtos", backref="produtos_estoques")
    deposito: Mapped["ProdutosDepositos"] = relationship(
        "ProdutosDepositos", backref="produtos_estoques")


class ProdutoFornecedor(Base):  # 23
    """Produto por fornecedor."""

    __tablename__ = "produto_fornecedor"

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    descricao: Mapped[str] = mapped_column(String(150))
    codigo: Mapped[str] = mapped_column(String(20))
    preco_custo: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_compra: Mapped[int] = mapped_column(Integer, nullable=False)
    padrao: Mapped[bool] = mapped_column(Boolean, nullable=False)
    id_produto: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos.id_bling"), nullable=False)
    id_fornecedor: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contatos.id_bling"))

    produto: Mapped["Produtos"] = relationship(
        "Produtos", backref="produto_fornecedor")
    fornecedor: Mapped["Contatos"] = relationship(
        "Contatos", backref="produto_fornecedor")


class ProdutoVariacao(Base):  # 24
    """Variação do produto."""

    __tablename__ = "produto_variacao"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    id_produto_pai: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos.id_bling"), nullable=False)
    id_produto_filho: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos.id_bling"), nullable=False,
        unique=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    clone_pai: Mapped[bool] = mapped_column(Boolean, nullable=False)

    produto_pai: Mapped["Produtos"] = relationship(
        "Produtos", backref="produto_variacao")
    produto_filho: Mapped["Produtos"] = relationship(
        "Produtos", backref="produto_variacao")


class ProdutosMidiasRelacao(Base):  # 25
    """Relação das mídias dos produtos."""

    __tablename__ = "produtos_midias_relacao"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    id_produto: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos.id_bling"), nullable=False)
    id_image: Mapped[int] = mapped_column(
        Integer, ForeignKey("produtos_midias.id", ondelete='CASCADE'),
        nullable=False)

    produto: Mapped["Produtos"] = relationship(
        "Produtos", backref="produtos")
    image: Mapped["ProdutosMidias"] = relationship(
        "ProdutosMidias", backref="produtos_midias_relacao")


# ===============================
# ========CONTAS RECEBER=========
# ===============================


class ContasContabeis(Base):  # 26
    """Contas contabeis."""

    __tablename__ = "contas_contabeis"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    nome: Mapped[str] = mapped_column(String(45), nullable=False)


class CategoriasReceitasDespesasTipo(Base):  # 27
    """Tipo das categorias de receitas e despesas."""

    __tablename__ = "categorias_receitas_despesas_tipo"
    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(25), nullable=False,
                                      comment=("`1` Despesa\n"
                                               "`2` Receita\n"
                                               "`3` Receita e despesa"
                                               ))


class CategoriasReceitasDespesas(Base):  # 28
    """Categorias de receitas e despesas."""

    __tablename__ = "categorias_receitas_despesas"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    nome: Mapped[str] = mapped_column(String(45), nullable=False)
    id_tipo: Mapped[int] = mapped_column(
        Integer, ForeignKey("categorias_receitas_despesas_tipo.id"),
        nullable=False, comment=("`1` Despesa"
                                 "`2` Receita"
                                 "`3` Receita e despesa'"))
    situacao: Mapped[bool] = mapped_column(Boolean, nullable=False)

    tipo: Mapped["CategoriasReceitasDespesasTipo"] = relationship(
        "CategoriasReceitasDespesasTipo",
        backref="categorias_receitas_despesas")


class CategoriasReceitasDespesasRelacao(Base):  # 29
    """Relação entre as categorias de receita e despesas."""

    __tablename__ = "categorias_receitas_despesas_relacao"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    id_categoria_pai: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("categorias_receitas_despesas.id_bling"),
        nullable=False)
    id_categoria_filho: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("categorias_receitas_despesas.id_bling"),
        nullable=False, unique=True)

    categoria_pai: Mapped["CategoriasReceitasDespesas"] = relationship(
        "CategoriasReceitasDespesas",
        backref="categorias_receitas_despesas_relacao")
    categoria_filho: Mapped["CategoriasReceitasDespesas"] = relationship(
        "CategoriasReceitasDespesas",
        backref="categorias_receitas_despesas_relacao")


class ContasSituacao(Base):  # 30
    """Situação das contas."""

    __tablename__ = "contas_situacao"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(String(45), nullable=False,
                                      comment=("`1` Em aberto"
                                               "`2` Recebido"
                                               "`3` Parcialmente recebido"
                                               "`4` Devolvido"
                                               "`5` Cancelado"))


class TiposPagamento(Base):  # 31
    """Tipos de pagamento."""

    __tablename__ = "tipos_pagamento"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(
        String(127), nullable=False,
        comment=("`1` Dinheiro"
                 "`2` Cheque"
                 "`3` Cartão de Crédito"
                 "`4` Cartão de Débito"
                 "`5` Crédito Loja"
                 "`10` Vale Alimentação"
                 "`11` Vale Refeição"
                 "`12` Vale Presente"
                 "`13` Vale Combustível"
                 "`14` Duplicata Mercantil"
                 "`15` Boleto Bancário"
                 "`16` Depósito Bancário"
                 "`17` Pagamento Instantâneo (PIX)"
                 "`18` Transferência Bancária, Carteira Digital"
                 "`19` Programa de Fidelidade, Cashback, Crédito Virtual"
                 "`90` Sem pagamento"
                 "`99` Outros"))


class FormasPagamentoPadrao(Base):  # 32
    """O padrão da forma de pagamento."""

    __tablename__ = "formas_pagamento_padrao"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(String(16), nullable=False,
                                      comment=("`1` Pagamentos"
                                               "`2` Recebimentos"
                                               "`3` Pagamentos e Recebimentos")
                                      )


class FormasPagamentoDestino(Base):  # 33
    """Destino da forma de pagamento."""

    __tablename__ = "formas_pagamento_destino"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(String(22), nullable=False,
                                      comment=("`1` Conta a receber/pagar"
                                               "`2` Ficha financeira"
                                               "`3` Caixa e bancos"))


class FormasPagamentoFinalidade(Base):  # 34
    """Finalidade da forma de pagamento."""

    __tablename__ = "formas_pagamento_finalidade"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(String(26), nullable=False,
                                      comment=("`1` Pagamentos"
                                               "`2` Recebimentos"
                                               "`3` Pagamentos e Recebimentos")
                                      )


class FormasPagamento(Base):  # 35
    """Formas de pagamentos do Bling."""

    __tablename__ = "formas_pagamento"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    nome: Mapped[str] = mapped_column(String(45), nullable=False)

    id_tipo_pagamento: Mapped[int] = mapped_column(
        Integer, ForeignKey("tipos_pagamento.id"), nullable=False)

    situacao: Mapped[bool] = mapped_column(Boolean, nullable=False,
                                           comment=("`0` Inativa\n"
                                                    "`1` Ativa'"))
    fixa: Mapped[bool] = mapped_column(Boolean, nullable=False)

    id_padrao: Mapped[int] = mapped_column(
        Integer, ForeignKey("formas_pagamento_padrao.id"), nullable=False,
        comment=("`0` Não\n`1` Padrão\n`2` Padrão devolução"))

    condicao: Mapped[str] = mapped_column(String(127), nullable=False)

    id_destino: Mapped[int] = mapped_column(
        Integer, ForeignKey("formas_pagamento_destino.id"), nullable=False)

    id_finalidade: Mapped[int] = mapped_column(
        Integer, ForeignKey("formas_pagamento_finalidade.id"), nullable=False)

    taxas_aliquota: Mapped[int] = mapped_column(Integer, nullable=False)
    taxas_valor: Mapped[int] = mapped_column(Integer, nullable=False)
    taxas_prazo: Mapped[int] = mapped_column(Integer, nullable=False)

    tipo_pagamento: Mapped["TiposPagamento"] = relationship(
        "TiposPagamento", backref="formas_pagamento")
    padrao: Mapped["FormasPagamentoPadrao"] = relationship(
        "FormasPagamentoPadrao", backref="formas_pagamento")
    destino: Mapped["FormasPagamentoDestino"] = relationship(
        "FormasPagamentoDestino", backref="formas_pagamento")
    finalidade: Mapped["FormasPagamentoFinalidade"] = relationship(
        "FormasPagamentoFinalidade", backref="formas_pagamento")


class ContasTipoOcorrencia(Base):  # 36
    """Tipo de ocorrência/frequencia da conta."""

    __tablename__ = "contas_tipo_ocorrencia"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(String(12), nullable=False,
                                      comment=("`1` Única\n`2` Parcelada\n"
                                               "`3` Mensal\n`4` Bimestral\n"
                                               "`5` Trimestral\n"
                                               "`6` Semestral\n`7` Anual\n"
                                               "`8` Quinzenal\n`9` Semanal"))


class Vendedores(Base):  # 37
    """Vendedores."""

    __tablename__ = "vendedores"

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    desconto_limite: Mapped[int] = mapped_column(Integer, nullable=False)
    id_loja: Mapped[int] = mapped_column(Integer, nullable=False)
    comissoes_desconto_maximo: Mapped[int] = mapped_column(Integer,
                                                           nullable=False)
    comissoes_aliquota: Mapped[int] = mapped_column(Integer, nullable=False)
    id_contato: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contatos.id_bling"), nullable=False)

    contato: Mapped["Contatos"] = relationship(
        "Contatos", backref="vendedores")


class ContasReceitasDespesas(Base):  # 38
    """Contas de receitas ou despesas."""

    __tablename__ = "contas_receitas_despesas"

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)

    id_situacao: Mapped[int] = mapped_column(
        Integer, ForeignKey("contas_situacao.id"))

    vencimento: Mapped[date] = mapped_column(Date, nullable=False)
    valor: Mapped[int] = mapped_column(Integer, nullable=False)
    id_transacao: Mapped[str] = mapped_column(String(63))
    link_qr_code_pix: Mapped[str] = mapped_column(Text)
    link_boleto: Mapped[str] = mapped_column(Text)
    data_emissao: Mapped[date] = mapped_column(Date, nullable=False,
                                               server_default=text("NOW()"))

    id_contato: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contatos.id_bling"), nullable=False)

    id_forma_pagamento: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("formas_pagamento.id_bling"))

    saldo: Mapped[int] = mapped_column(Integer, nullable=False,
                                       comment=("É calculado subtraindo os"
                                                "valores dos recebimentos do"
                                                "valor da conta"))
    vencimento_original: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("NOW()"))
    numero_documento: Mapped[str] = mapped_column(
        String(63), comment="Número para controle interno da empresa")
    competencia: Mapped[date] = mapped_column(Date, nullable=False)
    historico: Mapped[str] = mapped_column(Text, nullable=False,
                                           comment=("Descriçao da conta para "
                                                    "controle interno da "
                                                    "empresa"))
    numero_banco: Mapped[str] = mapped_column(
        String(63), comment=("Adicionado automaticamente com o número "
                             "preenchido no cadastro do banco"))

    id_portador: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contas_contabeis.id_bling"))

    id_categoria_receita_despesa: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("categorias_receitas_despesas.id_bling"),
        nullable=False)

    id_vendedor: Mapped[int] = mapped_column(BigInteger,
                                             ForeignKey("vendedores.id_bling"))

    id_tipo_ocorrencia: Mapped[int] = mapped_column(
        Integer, ForeignKey("contas_tipo_ocorrencia.id"),
        comment=("`1` Única\n`2` Parcelada\n`3` Mensal\n`4` Bimestral\n"
                 "`5` Trimestral\n`6` Semestral\n`7` Anual\n`8` Quinzenal\n"
                 "`9` Semanal'"))

    considerar_dias_uteis: Mapped[bool] = mapped_column(Boolean)
    dia_vencimento: Mapped[date] = mapped_column(Date,
                                                 server_default=text("NOW()"))
    numero_parcelas: Mapped[int] = mapped_column(Integer)
    data_limite: Mapped[date] = mapped_column(Date,
                                              server_default=text("NOW()"))
    alterado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("current_timestamp"))

    situacao: Mapped["ContasSituacao"] = relationship(
        "ContasSituacao", backref="contas_receitas_despesas")
    contato: Mapped["Contatos"] = relationship(
        "Contatos", backref="contas_receitas_despesas")
    forma_pagamento: Mapped["FormasPagamento"] = relationship(
        "FormasPagamento", backref="contas_receitas_despesas")
    portador: Mapped["ContasContabeis"] = relationship(
        "ContasContabeis", backref="contas_receitas_despesas")
    categoria_receita_despesa: Mapped["CategoriasReceitasDespesas"] = (
        relationship("CategoriasReceitasDespesas",
                     backref="contas_receitas_despesas"))
    vendedor: Mapped["Vendedores"] = relationship(
        "Vendedores", backref="contas_receitas_despesas")
    tipo_ocorrencia: Mapped["ContasTipoOcorrencia"] = relationship(
        "ContasTipoOcorrencia", backref="contas_receitas_despesas")


class ContasOrigemSituacoes(Base):  # 39
    """Situação das contas."""

    __tablename__ = "contas_origem_situacoes"

    id: Mapped[int] = mapped_column(
        Integer, Identity(), primary_key=True, nullable=False,
        comment=("Situações da venda:\n`0` Em aberto\n`1` Atendido\n"
                 "`2` Cancelado\n`3` Em andamento\n`5` Faturado parcialmente\n"
                 "`6` Atendido parcialmente\n`7` Aguardando pagamento\n"
                 "`8` Pagamento confirmado\n`10` Em digitação\n`11` Verificado"
                 "\n`12` Checkout parcial"))
    nome: Mapped[str] = mapped_column(String(31), nullable=False)


class ContasOrigens(Base):  # 40
    """Contas origens."""

    __tablename__ = "contas_origens"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    id_origem: Mapped[int] = mapped_column(BigInteger, nullable=False)

    id_conta: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contas_receitas_despesas.id_bling",
                               ondelete='CASCADE'), nullable=False)

    tipo_origem: Mapped[str] = mapped_column(String(63))
    numero: Mapped[str] = mapped_column(String(63))
    data_emissao: Mapped[date] = mapped_column(Date)
    valor: Mapped[int] = mapped_column(Integer, nullable=False)
    id_conta_origem_situacao: Mapped[int] = mapped_column(
        Integer, ForeignKey("contas_origem_situacoes.id"), nullable=False)
    url: Mapped[str] = mapped_column(Text)

    conta: Mapped["ContasReceitasDespesas"] = relationship(
        "ContasReceitasDespesas", backref="contas_origens")
    conta_origem_situacao: Mapped["ContasOrigemSituacoes"] = relationship(
        "ContasOrigemSituacoes", backref="contas_origens")


class Borderos(Base):  # 41
    """Borderos."""

    __tablename__ = "borderos"

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    historico: Mapped[str] = mapped_column(Text)

    id_portador: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contas_contabeis.id_bling"), nullable=False)

    id_categoria_receita_despesa: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("categorias_receitas_despesas.id_bling"),
        nullable=False)

    portador: Mapped["ContasContabeis"] = relationship(
        "ContasContabeis", backref="borderos")
    categoria_receita_despesa: Mapped["CategoriasReceitasDespesas"] = (
        relationship("CategoriasReceitasDespesas", backref="borderos"))


class Pagamentos(Base):  # 42
    """Pagamentos."""

    __tablename__ = "pagamentos"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)

    id_bordero: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("borderos.id_bling", ondelete='CASCADE'),
        nullable=False)

    id_contato: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contatos.id_bling"), nullable=False)

    numero_documento: Mapped[str] = mapped_column(String(63))
    valor_pago: Mapped[int] = mapped_column(Integer, nullable=False)
    juros: Mapped[int] = mapped_column(Integer, nullable=False)
    desconto: Mapped[int] = mapped_column(Integer, nullable=False)
    acrescimo: Mapped[int] = mapped_column(Integer, nullable=False)
    tarifa: Mapped[int] = mapped_column(Integer, nullable=False)

    bordero: Mapped["Borderos"] = relationship(
        "Borderos", backref="pagamentos")
    contato: Mapped["Contatos"] = relationship(
        "Contatos", backref="pagamentos")


class ContasBorderosRelacao(Base):  # 43
    """Relação dos borderos das contas."""

    __tablename__ = "contas_borderos_relacao"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)

    id_conta: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contas_receitas_despesas.id_bling",
                               ondelete='CASCADE'), nullable=False)

    id_bordero: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("borderos.id_bling", ondelete='CASCADE'),
        nullable=False)

    conta: Mapped["ContasReceitasDespesas"] = relationship(
        "ContasReceitasDespesas", backref="contas_borderos_relacao")
    bordero: Mapped["Borderos"] = relationship(
        "Borderos", backref="contas_borderos_relacao")


# ===============================
# ============VENDAS=============
# ===============================


class Modulos(Base):  # 44
    """Módulos do Bling."""

    __tablename__ = "modulos"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
        CheckConstraint("descricao <> ''"),
    )

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    nome: Mapped[str] = mapped_column(String(45), nullable=False)
    descricao: Mapped[str] = mapped_column(String(120), nullable=False)
    criar_situacoes: Mapped[bool] = mapped_column(Boolean, nullable=False)


class Situacoes(Base):  # 45
    """Situações."""

    __tablename__ = "situacoes"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
        CheckConstraint("cor <> ''"),
    )

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    id_modulo: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("modulos.id_bling"), nullable=False)
    nome: Mapped[str] = mapped_column(String(45), nullable=False)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)

    modulo: Mapped["Modulos"] = relationship(
        "Modulos", backref="situacoes")


class TransporteFretePorContaDe(Base):  # 46
    """Transporte do pedido por conta de."""

    __tablename__ = "transporte_frete_por_conta_de"

    __table_args__ = (
        CheckConstraint("nome <> ''"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(
        String(63), nullable=False,
        comment=("`0` Contratação do Frete por conta do Remetente (CIF)"
                 "`1` Contratação do Frete por conta do Destinatário (FOB)"
                 "`2` Contratação do Frete por conta de Terceiros"
                 "`3` Transporte Próprio por conta do Remetente"
                 "`4` Transporte Próprio por conta do Destinatário"
                 "`9` Sem Ocorrência de Transporte."))


class TransporteEtiqueta(Base):  # 47
    """Etiqueta de transporte."""

    __tablename__ = "transporte_etiqueta"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    nome: Mapped[str] = mapped_column(String(63))
    id_endereco: Mapped[int] = mapped_column(
        Integer, ForeignKey("enderecos.id"), nullable=False)

    endereco: Mapped["Enderecos"] = relationship(
        "Enderecos", backref="transporte_etiqueta")


class Vendas(Base):  # 48
    """Pedidos de vendas."""

    __tablename__ = "vendas"

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_loja: Mapped[str] = mapped_column(String(45))
    data: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=text("current_timestamp"),
        comment=("Valor obrigatório caso parâmetro de "
                 "geração de parcelas seja este"))
    data_saida: Mapped[date] = mapped_column(
        Date, server_default=text("NOW()"),
        comment=("Valor obrigatório caso parâmetro de "
                 "geração de parcelas seja este"))
    data_prevista: Mapped[date] = mapped_column(
        Date, comment=("Valor obrigatório caso parâmetro de "
                       "geração de parcelas seja este"))

    id_contato: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contatos.id_bling"), nullable=False)

    id_situacao: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("situacoes.id_bling"), nullable=False)

    situacao_valor: Mapped[int] = mapped_column(Integer, nullable=False)

    id_loja: Mapped[int] = mapped_column(
        Integer, ForeignKey("canais_vendas.id_bling"), nullable=False)

    numero_pedido_compra: Mapped[str] = mapped_column(
        String(45), comment='Número da ordem de compra do pedido.')
    outras_despesas: Mapped[int] = mapped_column(Integer, nullable=False)
    observacoes: Mapped[str] = mapped_column(Text)
    observacoes_internas: Mapped[str] = mapped_column(Text)
    desconto: Mapped[int] = mapped_column(Integer, nullable=False)
    desconto_unidade: Mapped[str] = mapped_column(
        String(12), nullable=False, comment='0 - Real\n1 - Percentual')

    id_categoria: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("categorias_receitas_despesas.id_bling"))

    id_nota_fiscal: Mapped[int] = mapped_column(BigInteger)
    total_icms: Mapped[int] = mapped_column(Integer)
    total_ipi: Mapped[int] = mapped_column(Integer)

    id_vendedor: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("vendedores.id_bling"))

    transporte_id_frete_por_conta: Mapped[int] = mapped_column(
        Integer, ForeignKey("transporte_frete_por_conta_de.id"),
        nullable=False)

    transporte_valor_frete: Mapped[int] = mapped_column(
        Integer, nullable=False)
    transporte_quantidade_volumes: Mapped[int] = mapped_column(Integer)
    transporte_peso_bruto: Mapped[int] = mapped_column(Integer)
    transporte_prazo_entrega: Mapped[int] = mapped_column(Integer)

    transporte_id_contato: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contatos.id_bling"), comment='transportador')

    transporte_id_etiqueta: Mapped[int] = mapped_column(
        Integer, ForeignKey("transporte_etiqueta.id"))

    intermediador_cnpj: Mapped[str] = mapped_column(String(14), nullable=False)
    intermediador_nome_usuario: Mapped[str] = mapped_column(
        String(63), nullable=False)
    taxa_comissao: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Taxa de comissão perante ao total da venda.")
    taxa_custo_frete: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Valor de custo do frete.")
    taxa_valor_base: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment=("Valor base da venda para demonstrativo de cálculo "
                 "das taxas via interface (Se não informado considera o total"
                 " da venda)."))
    alterado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("current_timestamp"))

    contato: Mapped["Contatos"] = relationship(
        "Contatos", backref="vendas")
    situacao: Mapped["Situacoes"] = relationship(
        "Situacoes", backref="vendas")
    loja: Mapped["CanaisVendas"] = relationship(
        "CanaisVendas", backref="vendas")
    categoria: Mapped["CategoriasReceitasDespesas"] = relationship(
        "CategoriasReceitasDespesas", backref="vendas")
    vendedor: Mapped["Vendedores"] = relationship(
        "Vendedores", backref="vendas")
    transporte_frete_por_conta_de: Mapped["TransporteFretePorContaDe"] = (
        relationship("TransporteFretePorContaDe", backref="vendas"))
    contato: Mapped["Contatos"] = relationship(
        "Contatos", backref="vendas")
    transporte_etiqueta: Mapped["TransporteEtiqueta"] = relationship(
        "TransporteEtiqueta", backref="vendas")


class TransporteVolumes(Base):  # 49
    """Volumes do transporte."""

    __tablename__ = "transporte_volumes"

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)

    id_venda: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("vendas.id_bling"), nullable=False)

    id_logistica_servico: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("logistica_servicos.id_bling"), nullable=False)

    codigo_rastreamento: Mapped[str] = mapped_column(String(45))

    venda: Mapped["Vendas"] = relationship(
        "Vendas", backref="transporte_volumes")
    logistica_servico: Mapped["LogisticaServicos"] = relationship(
        "LogisticaServicos", backref="transporte_volumes")


class VendasItensProdutos(Base):  # 50
    """Produtos do pedido de venda."""

    __tablename__ = "vendas_itens_produtos"

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)

    id_venda: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("vendas.id_bling"), nullable=False)

    id_produto: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos.id_bling"))

    desconto: Mapped[int] = mapped_column(Integer, nullable=False,
                                          comment="Percentual")
    valor: Mapped[int] = mapped_column(Integer, nullable=False,
                                       comment=("Valor unitário do item. Preço"
                                                " de lista = 4.9 (valor) + 2% "
                                                "(desconto)"))
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)

    venda: Mapped["Vendas"] = relationship(
        "Vendas", backref="vendas_itens_produtos")
    produto: Mapped["Produtos"] = relationship(
        "Produtos", backref="vendas_itens_produtos")


class Parcelas(Base):  # 51
    """Parcelas do pedido de vendas."""

    __tablename__ = "parcelas"

    id_bling: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, nullable=False,
        comment="id contas a receber")

    id_venda: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("vendas.id_bling"), nullable=False)

    data_vencimento: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("NOW()"))
    valor: Mapped[int] = mapped_column(Integer, nullable=False)
    observacoes: Mapped[str] = mapped_column(String(120))

    id_forma_pagamento: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("formas_pagamento.id_bling"), nullable=False)

    id_conta_receber: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contas_receitas_despesas.id_bling",
                               ondelete='CASCADE'))

    venda: Mapped["Vendas"] = relationship(
        "Vendas", backref="parcelas")
    forma_pagamento: Mapped["FormasPagamento"] = relationship(
        "FormasPagamento", backref="parcelas")
    conta_receber: Mapped["ContasReceitasDespesas"] = relationship(
        "ContasReceitasDespesas", backref="parcelas")


class CanaisVendas(Base):  # 52
    """Canais de vendas."""

    __tablename__ = "canais_vendas"

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String(63), nullable=False)
    situacao: Mapped[int] = mapped_column(Integer, nullable=False)


class CanaisVendasFiliais(Base):  # 53
    """Filiais dos canais de vendas."""

    __tablename__ = "canais_vendas_filiais"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)

    id_canal_venda: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("canais_vendas.id_bling"), nullable=False)

    cnpj: Mapped[str] = mapped_column(String(15), nullable=False)
    unidade_negocio: Mapped[str] = mapped_column(Text, nullable=False)

    id_deposito: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos_depositos.id_bling"), nullable=False)

    padrao: Mapped[bool] = mapped_column(Boolean, nullable=False)

    canal_venda: Mapped["CanaisVendas"] = relationship(
        "CanaisVendas", backref="canais_vendas_filiais")
    deposito: Mapped["ProdutosDepositos"] = relationship(
        "ProdutosDepositos", backref="canais_vendas_filiais")


class Logisticas(Base):  # 54
    """Logisticas de entrega."""

    __tablename__ = "logisticas"

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_integracao: Mapped[str] = mapped_column(String(100), nullable=False)
    integracao_nativa: Mapped[bool] = mapped_column(Boolean, nullable=False)
    situacao: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment=("Situação do canal de venda\n`TRUE` "
                                          "Habilitado\n`FALSE` Desabilitado"))
    integracao_id: Mapped[Optional[int]] = mapped_column(BigInteger)


class LogisticaServicos(Base):  # 55
    """Serviços de logistica."""

    __tablename__ = "logistica_servicos"

    id_bling: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                          nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    frete_item: Mapped[int] = mapped_column(Integer, nullable=False)
    estimativa_entrega: Mapped[int] = mapped_column(Integer, nullable=False)
    id_codigo_servico: Mapped[str] = mapped_column(String(100), nullable=False)

    logistica_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("logisticas.id_bling"), nullable=False)

    transportador_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contatos.id_bling"), nullable=False)

    logistica: Mapped["Logisticas"] = relationship(
        "Logistica", backref="logistica_servicos")
    transportador: Mapped["Contatos"] = relationship(
        "Contatos", backref="logistica_servicos")


class LogisticaServicoAliases(Base):  # 56
    """Aliases de serviços da logistica."""

    __tablename__ = "logistica_servico_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    servico_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("logistica_servicos.id_bling"), nullable=False)
    alias: Mapped[str] = mapped_column(String(255), nullable=False)

    servico: Mapped["LogisticaServicos"] = relationship(
        "LogisticaServicos", backref="logistica_servico_aliases")


class AtualizacoesModulos(Base):  # 57
    """Registro de atualizações dos módulos."""

    __tablename__ = "atualizacoes_modulos"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)
    datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=text("current_timestamp"))


class ContagemEstoque(Base):  # 58
    """Contagem de Estoque."""

    __tablename__ = "contagem_estoque"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)

    id_produto: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos.id_bling"), nullable=False,
        unique=True)

    codigo: Mapped[str] = mapped_column(String(120), nullable=False)
    quantidade_lida: Mapped[int] = mapped_column(Integer, nullable=False)
    datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=text("current_timestamp"))

    produto: Mapped["Produtos"] = relationship(
        "Produtos", backref="contagem_estoque")


class RegistrosDeEstoque(Base):  # 59
    """Registros de estoque."""

    __tablename__ = "registros_de_estoque"

    id_bling: Mapped[int] = mapped_column(
        Integer, Identity(), primary_key=True, nullable=False)

    id_produto: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos.id_bling"), nullable=False)

    id_deposito: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos_depositos.id_bling"), nullable=False)

    operacao: Mapped[str] = mapped_column(CHAR(1), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    preco: Mapped[int] = mapped_column(Integer, nullable=False)
    custo: Mapped[int] = mapped_column(Integer, nullable=False)
    observacoes: Mapped[str] = mapped_column(String(100), nullable=False)
    datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=text("current_timestamp"))

    produto: Mapped["Produtos"] = relationship(
        "Produtos", backref="registros_de_estoque")
    deposito: Mapped["ProdutosDepositos"] = relationship(
        "ProdutosDepositos", backref="registros_de_estoque")


class RegistrosDeComparacaoBalanco(Base):  # 60
    """Registro de comparação do balanço."""

    __tablename__ = "registros_de_comparacao_balanco"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True,
                                    nullable=False)

    id_produto: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos.id_bling"), nullable=False)

    id_deposito: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("produtos_depositos.id_bling"), nullable=False)

    saldo_antes: Mapped[int] = mapped_column(Integer, nullable=False)
    saldo_depois: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False,
                                       server_default=text("NOW()"))

    produto: Mapped["Produtos"] = relationship(
        "Produtos", backref="registros_de_comparacao_balanco")
    deposito: Mapped["ProdutosDepositos"] = relationship(
        "ProdutosDepositos", backref="registros_de_comparacao_balanco")
