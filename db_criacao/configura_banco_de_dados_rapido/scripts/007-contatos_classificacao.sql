CREATE TABLE "contatos_classificacao"(
    "id_bling"  BIGINT PRIMARY KEY  NOT NULL,
    "nome"      VARCHAR(63)         NOT NULL UNIQUE CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "contatos_classificacao"."nome" IS 'Fornecedor etc';
