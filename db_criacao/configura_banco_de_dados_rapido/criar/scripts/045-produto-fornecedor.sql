CREATE TABLE "produto_fornecedor"(
    "id_bling"      BIGINT PRIMARY KEY  NOT NULL,
    "descricao"     VARCHAR(150),
    "codigo"        VARCHAR(20),
    "preco_custo"   INTEGER             NOT NULL,
    "preco_compra"  INTEGER             NOT NULL,
    "padrao"        BOOLEAN             NOT NULL,
    "id_produto"    BIGINT              NOT NULL REFERENCES "produtos"("id_bling"),
    "id_fornecedor" BIGINT              REFERENCES "contatos"("id_bling")
);
