CREATE TABLE "produtos_estoques"(
    "id"            SERIAL PRIMARY KEY  NOT NULL,
    "id_produto"    BIGINT              NOT NULL REFERENCES "produtos"("id_bling"),
    "id_deposito"   BIGINT              NOT NULL REFERENCES "produtos_depositos"("id_bling"),
    "saldo_fisico"  INTEGER             NOT NULL,
    "saldo_virtual" INTEGER             NOT NULL
);
