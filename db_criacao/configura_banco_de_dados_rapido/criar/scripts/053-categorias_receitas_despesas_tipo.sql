CREATE TABLE "categorias_receitas_despesas_tipo"(
    "id"    BIGINT PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(25)         NOT NULL CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "categorias_receitas_despesas_tipo"."nome" IS '`1` Despesa
    `2` Receita
    `3` Receita e despesa';
