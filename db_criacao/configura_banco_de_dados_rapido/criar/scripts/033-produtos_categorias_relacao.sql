CREATE TABLE "produtos_categorias_relacao"(
    "id"                    SERIAL PRIMARY KEY  NOT NULL,
    "id_categoria_pai"      BIGINT              NOT NULL REFERENCES "produtos_categorias"("id_bling"),
    "id_categoria_filho"    BIGINT              NOT NULL UNIQUE REFERENCES "produtos_categorias"("id_bling")
);
