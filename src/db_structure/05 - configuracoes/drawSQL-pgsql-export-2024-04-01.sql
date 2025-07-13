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

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "registros_de_estoque"(
        "id_bling"      SERIAL       PRIMARY KEY NOT NULL
    ,   "id_produto"    BIGINT                   NOT NULL REFERENCES "produtos"("id_bling")
    ,   "id_deposito"   BIGINT                   NOT NULL REFERENCES "produtos_depositos"("id_bling")
    ,   "operacao"      CHAR(1)                  NOT NULL
    ,   "quantidade"    INTEGER                  NOT NULL
    ,   "preco"         INTEGER                  NOT NULL
    ,   "custo"         INTEGER                  NOT NULL
    ,   "observacoes"   VARCHAR(100)             NOT NULL
    ,   "datetime"      TIMESTAMPTZ              NOT NULL DEFAULT current_timestamp
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "registros_de_comparacao_balanco"(
        "id"            SERIAL       PRIMARY KEY NOT NULL
    ,   "id_produto"    BIGINT                   NOT NULL REFERENCES "produtos"("id_bling")
    ,   "id_deposito"   BIGINT                   NOT NULL REFERENCES "produtos_depositos"("id_bling")
    ,   "saldo_antes"   INTEGER                  NOT NULL
    ,   "saldo_depois"  INTEGER                  NOT NULL
    ,   "date"          DATE                     NOT NULL DEFAULT NOW()
);
