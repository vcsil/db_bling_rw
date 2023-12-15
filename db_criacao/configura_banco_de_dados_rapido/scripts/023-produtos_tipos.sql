CREATE TABLE "produtos_tipos"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(15)         NOT NULL UNIQUE CHECK ("nome" <> ''),
    "sigla" CHAR(1)             NOT NULL UNIQUE CHECK ("sigla" <> '')
);
COMMENT ON COLUMN
    "produtos_tipos"."nome" IS 'Tipo do produto
    `S` Serviço
    `P` Produto
    `N` Serviço 06 21 22';