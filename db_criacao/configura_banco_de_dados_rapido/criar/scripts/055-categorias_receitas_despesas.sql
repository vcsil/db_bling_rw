CREATE TABLE "categorias_receitas_despesas"(
    "id_bling"      BIGINT PRIMARY KEY  NOT NULL,
    "nome"          VARCHAR(45)         NOT NULL CHECK ("nome" <> ''),
    "id_tipo"       INTEGER          	NOT NULL REFERENCES "categorias_receitas_despesas_tipo"("id"),
    "situacao"	    BOOLEAN		NOT NULL
);
COMMENT ON COLUMN
    "categorias_receitas_despesas"."tipo" IS '`1` Despesa
    `2` Receita
    `3` Receita e despesa';
