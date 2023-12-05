CREATE TABLE "produtos_condicao"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(17)         NOT NULL
);
COMMENT ON COLUMN
    "produtos_condicao"."nome" IS 'Condição do produto
    `0` Não especificado
    `1` Novo
    `2` Usado"';
