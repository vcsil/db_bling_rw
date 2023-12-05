CREATE TABLE "produtos_tributacao"(
    "id"            SERIAL PRIMARY KEY  NOT NULL,
    "id_produto"    BIGINT              NOT NULL REFERENCES "produtos"("id_bling"),
    "ncm"           VARCHAR(10)         NOT NULL DEFAULT '7113.20.00',
    "cest"          VARCHAR(10)         NOT NULL DEFAULT '28.058.00'
);