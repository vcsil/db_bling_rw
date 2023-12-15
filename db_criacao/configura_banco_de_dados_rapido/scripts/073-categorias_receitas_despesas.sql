CREATE TABLE "categorias_receitas_despesas"(
    "id_bling"      BIGINT PRIMARY KEY  NOT NULL,
    "nome"          VARCHAR(45)         NOT NULL CHECK ("nome" <> ''),
    "tipo"          INTEGER             NOT NULL
);
COMMENT ON COLUMN
    "categorias_receitas_despesas"."tipo" IS '`1` Despesa
    `2` Receita
    `3` Receita e despesa';