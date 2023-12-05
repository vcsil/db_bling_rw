CREATE TABLE "produto_variacao"(
    "id"                SERIAL PRIMARY KEY  NOT NULL,
    "id_produto_pai"    BIGINT              NOT NULL REFERENCES "produtos"("id_bling"),
    "id_produto_filho"  BIGINT              NOT NULL UNIQUE REFERENCES "produtos"("id_bling"),
    "nome"              VARCHAR(120)        NOT NULL,
    "ordem"             INTEGER             NOT NULL,
    "clone_pai"         BOOLEAN             NOT NULL
);