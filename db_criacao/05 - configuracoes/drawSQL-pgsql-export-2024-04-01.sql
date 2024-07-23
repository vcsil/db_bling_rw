CREATE TABLE "atualizacoes_modulos"(
        "id"       SERIAL       PRIMARY KEY NOT NULL
    ,   "datetime" TIMESTAMPTZ              NOT NULL DEFAULT current_timestamp
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contagem_estoque"(
        "id"                SERIAL       PRIMARY KEY NOT NULL
    ,   "id_produto"        BIGINT                   NOT NULL UNIQUE REFERENCES "produtos"("id_bling")
    ,   "codigo"            VARCHAR(120)             NOT NULL
    ,   "quantidade_lida"   INTEGER                  NOT NULL
    ,   "datetime"          TIMESTAMPTZ              NOT NULL DEFAULT current_timestamp
);
