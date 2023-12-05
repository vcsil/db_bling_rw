CREATE TABLE "produtos_categorias_relacao"(
    "id"                SERIAL PRIMARY KEY  NOT NULL,
    "categoria_pai"     BIGINT              NOT NULL REFERENCES "produtos_categorias"("id_bling"),
    "categoria_filho"   BIGINT              NOT NULL UNIQUE REFERENCES "produtos_categorias"("id_bling")
);