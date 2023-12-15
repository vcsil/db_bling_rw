CREATE TABLE "produtos"(
    "id_bling"                  BIGINT PRIMARY KEY  NOT NULL,
    "nome"                      VARCHAR(120)        NOT NULL UNIQUE CHECK ("nome" <> ''),
    "codigo"                    VARCHAR(120)        NOT NULL UNIQUE CHECK ("codigo" <> ''),
    "preco"                     INTEGER             NOT NULL,
    "id_tipo_produto"           INTEGER             NOT NULL DEFAULT 2 REFERENCES "produtos_tipos"("id"),
    "situacao_produto"          BOOLEAN             NOT NULL DEFAULT TRUE,
    "id_formato_produto"        INTEGER             NOT NULL REFERENCES "produtos_formatos"("id"),
    "descricao_curta"           TEXT,
    "data_validade"             DATE,
    "unidade"                   VARCHAR(6)          NOT NULL DEFAULT 'UN'  CHECK ("unidade" <> ''),
    "peso_liquido"              INTEGER             NOT NULL DEFAULT 0,
    "peso_bruto"                INTEGER             NOT NULL DEFAULT 0,
    "volumes"                   INTEGER             NOT NULL DEFAULT 1,
    "itens_por_caixa"           INTEGER             NOT NULL DEFAULT 1,
    "gtin"                      VARCHAR(14),
    "gtin_embalagem"            VARCHAR(13),
    "id_tipo_producao"          INTEGER             NOT NULL DEFAULT 1 REFERENCES "produtos_tipo_producao"("id"),
    "id_condicao_producao"      INTEGER             NOT NULL REFERENCES "produtos_condicao"("id"),
    "frete_gratis"              BOOLEAN             NOT NULL DEFAULT FALSE,
    "marca"                     VARCHAR(45)         NOT NULL DEFAULT 'RW'  CHECK ("marca" <> ''),
    "descricao_complementar"    TEXT,
    "link_externo"              TEXT,
    "observacoes"               TEXT,
    "id_categoria_produto"      INTEGER             NOT NULL REFERENCES "produtos_categorias"("id_bling"),
    "estoque_minimo"            INTEGER             NOT NULL DEFAULT 0,
    "estoque_maximo"            INTEGER             NOT NULL DEFAULT 0,
    "estoque_crossdocking"      INTEGER             NOT NULL DEFAULT 0,
    "estoque_localizacao"       VARCHAR(45),
    "id_dimensoes"              INTEGER             NOT NULL REFERENCES "dimensoes"("id"),
    "id_midia_principal"        INTEGER             NOT NULL REFERENCES "produtos_midias"("id")

    , CONSTRAINT uq_nome_codigo UNIQUE ("nome", "codigo")
);
COMMENT ON COLUMN
    "produtos"."situacao_produto" IS 'Situação do produto
    `A` Ativo 
    `I` Inativo"';
COMMENT ON COLUMN
    "produtos"."peso_liquido" IS 'Peso líquido em KG';
COMMENT ON COLUMN
    "produtos"."peso_bruto" IS 'Peso líquido em KG';
COMMENT ON COLUMN
    "produtos"."volumes" IS 'Quantidade total de volumes que o produto precisa ser dividido para entrega';
COMMENT ON COLUMN
    "produtos"."itens_por_caixa" IS 'Quantidade de itens por caixa/embalagem';
COMMENT ON COLUMN
    "produtos"."gtin" IS 'Código GTIN (GTIN-8, GTIN-12, GTIN-13 ou GTIN-14) do produto que está sendo comercializado';
COMMENT ON COLUMN
    "produtos"."gtin_embalagem" IS 'Código GTIN (GTIN-8, GTIN-12 ou GTIN-13) da menor unidade comercializada no varejo';
COMMENT ON COLUMN
    "produtos"."frete_gratis" IS 'Frete grátis
    Valor default: `false`';