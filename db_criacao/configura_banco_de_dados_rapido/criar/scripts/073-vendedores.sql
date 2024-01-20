CREATE TABLE "vendedores"(
        "id_bling"                  BIGINT PRIMARY KEY  NOT NULL
    ,   "desconto_limite"           INTEGER             NOT NULL
    ,   "id_loja"                   INTEGER             NOT NULL
    ,   "comissoes_desconto_maximo" INTEGER             NOT NULL
    ,   "comissoes_aliquota"        INTEGER             NOT NULL
    ,   "id_contato"                BIGINT              NOT NULL REFERENCES "contatos"("id_bling")
);