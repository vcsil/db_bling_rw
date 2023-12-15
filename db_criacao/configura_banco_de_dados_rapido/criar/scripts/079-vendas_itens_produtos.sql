CREATE TABLE "vendas_itens_produtos"(
    "id"            SERIAL PRIMARY KEY  NOT NULL,
    "id_venda"      BIGINT              NOT NULL REFERENCES "vendas"("id_bling"),
    "id_produto"    BIGINT              NOT NULL REFERENCES "produtos"("id_bling"),
    "desconto"      INTEGER             NOT NULL,
    "valor"         INTEGER             NOT NULL,
    "quantidade"    INTEGER             NOT NULL
);
COMMENT ON COLUMN
    "vendas_itens_produtos"."desconto" IS 'Percentual';
COMMENT ON COLUMN
    "vendas_itens_produtos"."valor" IS 'Valor unitário do item. Preço de lista = 4.9 (valor) + 2% (desconto)';