--------------------------------------------------------
--------------------#   PRODUTOS   #--------------------

CREATE TABLE "produtos_tipos"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(20)         NOT NULL UNIQUE CHECK ("nome" <> ''),
    "sigla" CHAR(1)             NOT NULL UNIQUE CHECK ("sigla" <> '')
);
COMMENT ON COLUMN
    "produtos_tipos"."nome" IS 'Tipo do produto
    `S` Serviço
    `P` Produto
    `N` Serviço 06 21 22';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_formatos"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(15)         NOT NULL UNIQUE CHECK ("nome" <> ''),
    "sigla" CHAR(1)             NOT NULL UNIQUE CHECK ("sigla" <> '')
);
COMMENT ON COLUMN
    "produtos_formatos"."nome" IS 'Formato do produto
    `S` Simples
    `V` Com variações
    `E` Com composição';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_tipo_producao"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(10)         NOT NULL UNIQUE CHECK ("nome" <> ''),
    "sigla" CHAR(1)             NOT NULL UNIQUE CHECK ("sigla" <> '')
);
COMMENT ON COLUMN
    "produtos_tipo_producao"."nome" IS 'Tipo da produção
    `P` Própria
    `T` Terceiros"';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_condicao"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(17)         NOT NULL CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "produtos_condicao"."nome" IS 'Condição do produto
    `0` Não especificado
    `1` Novo
    `2` Usado"';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_categorias"(
    "id_bling"  BIGINT PRIMARY KEY  NOT NULL,
    "nome"      VARCHAR(120)        NOT NULL CHECK ("nome" <> '')
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_categorias_relacao"(
    "id"                    SERIAL PRIMARY KEY  NOT NULL,
    "id_categoria_pai"      BIGINT              NOT NULL REFERENCES "produtos_categorias"("id_bling"),
    "id_categoria_filho"    BIGINT              NOT NULL UNIQUE REFERENCES "produtos_categorias"("id_bling")
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "dimensoes"(
    "id"                SERIAL PRIMARY KEY  NOT NULL,
    "largura"           INTEGER             NOT NULL,
    "altura"            INTEGER             NOT NULL,
    "profundidade"      INTEGER             NOT NULL,
    "unidade_medida"    INTEGER             NOT NULL
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_midias"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "tipo"  BOOLEAN             NOT NULL,
    "url"   TEXT                NOT NULL CHECK ("url" <> '')
);
COMMENT ON COLUMN
    "produtos_midias"."tipo" IS 'True: Foto
    False: Video';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos"(
    "id_bling"                  BIGINT PRIMARY KEY  NOT NULL,
    "nome"                      VARCHAR(120)        NOT NULL CHECK ("nome" <> ''), --UNIQUE
    "codigo"                    VARCHAR(120)        NOT NULL CHECK ("codigo" <> ''),
    "preco"                     INTEGER             NOT NULL,
    "id_tipo_produto"           INTEGER             NOT NULL DEFAULT 2 REFERENCES "produtos_tipos"("id"),
    "situacao_produto"          VARCHAR(10)         NOT NULL DEFAULT "Ativo",
    "id_formato_produto"        INTEGER             NOT NULL REFERENCES "produtos_formatos"("id"),
    "id_produto_pai"		BIGINT		    DEFAULT NULL REFERENCES "produtos"("id_bling"),
    "descricao_curta"           TEXT,
    "data_validade"             DATE,
    "unidade"                   VARCHAR(6)          DEFAULT 'UN'  CHECK ("unidade" <> ''),
    "peso_liquido"              INTEGER             NOT NULL DEFAULT 1,
    "peso_bruto"                INTEGER             NOT NULL DEFAULT 1,
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
    "ncm"           		VARCHAR(10)         DEFAULT '7113.20.00' CHECK ("ncm" <> ''),
    "cest"          		VARCHAR(9)          DEFAULT '28.058.00' CHECK ("cest" <> ''),
    "id_midia_principal"        INTEGER             REFERENCES "produtos_midias"("id"),
    "criado_em"			TIMESTAMPTZ	    NOT NULL DEFAULT current_timestamp,
    "alterado_em"		TIMESTAMPTZ	    DEFAULT NULL

    --, CONSTRAINT uq_nome_codigo UNIQUE ("nome", "codigo", situacao_produto)
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

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_depositos"(
    "id_bling"              BIGINT PRIMARY KEY  NOT NULL,
    "descricao"             VARCHAR(45)         NOT NULL  CHECK ("descricao" <> ''),
    "situacao"              BOOLEAN             NOT NULL DEFAULT TRUE,
    "padrao"                BOOLEAN             NOT NULL DEFAULT TRUE,
    "desconsiderar_saldo"   BOOLEAN             NOT NULL DEFAULT FALSE
);
COMMENT ON COLUMN
    "produtos_depositos"."situacao" IS '`0` Inativo
    `1` Ativo';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_estoques"(
    "id"            SERIAL PRIMARY KEY  NOT NULL,
    "id_produto"    BIGINT              NOT NULL REFERENCES "produtos"("id_bling"),
    "id_deposito"   BIGINT              NOT NULL REFERENCES "produtos_depositos"("id_bling"),
    "saldo_fisico"  INTEGER             NOT NULL,
    "saldo_virtual" INTEGER             NOT NULL
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produto_fornecedor"(
    "id_bling"      BIGINT PRIMARY KEY  NOT NULL,
    "descricao"     VARCHAR(150),
    "codigo"        VARCHAR(20),
    "preco_custo"   INTEGER             NOT NULL,
    "preco_compra"  INTEGER             NOT NULL,
    "padrao"        BOOLEAN             NOT NULL,
    "id_produto"    BIGINT              NOT NULL REFERENCES "produtos"("id_bling"),
    "id_fornecedor" BIGINT              REFERENCES "contatos"("id_bling")
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produto_variacao"(
    "id"                SERIAL PRIMARY KEY  NOT NULL,
    "id_produto_pai"    BIGINT              NOT NULL REFERENCES "produtos"("id_bling"),
    "id_produto_filho"  BIGINT              NOT NULL UNIQUE REFERENCES "produtos"("id_bling"),
    "nome"              VARCHAR(120)        NOT NULL CHECK ("nome" <> ''),
    "ordem"             INTEGER             NOT NULL,
    "clone_pai"         BOOLEAN             NOT NULL
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_midias_relacao"(
    "id"            SERIAL PRIMARY KEY  NOT NULL,
    "id_produto"    BIGINT              NOT NULL REFERENCES "produtos"("id_bling"),
    "id_image"      INTEGER             NOT NULL REFERENCES "produtos_midias"("id")
);
