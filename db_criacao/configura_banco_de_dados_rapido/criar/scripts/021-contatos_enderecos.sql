CREATE TABLE "contatos_enderecos"(
    "id"            SERIAL PRIMARY KEY  NOT NULL,
    "id_contato"    BIGINT              NOT NULL REFERENCES "contatos"("id_bling"),
    "id_endereco"   INTEGER             NOT NULL REFERENCES "enderecos"("id"),
    "tipo_endereco" SMALLINT            NOT NULL
);
COMMENT ON TABLE
    "contatos_enderecos" IS '`0`: Geral \n `1`: Cobrança';