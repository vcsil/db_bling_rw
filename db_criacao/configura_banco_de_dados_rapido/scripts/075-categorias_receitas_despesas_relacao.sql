CREATE TABLE "categorias_receitas_despesas_relacao"(
    "id"                    SERIAL PRIMARY KEY  NOT NULL,
    "id_categoria_pai"      BIGINT              NOT NULL REFERENCES "categorias_receitas_despesas"("id_bling"),
    "id_categoria_filho"    BIGINT              NOT NULL UNIQUE REFERENCES "categorias_receitas_despesas"("id_bling")
);