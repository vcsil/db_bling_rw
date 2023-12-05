CREATE TABLE "contatos_situacao"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(20)         NOT NULL,
    "sigla" CHAR(1)             NOT NULL
);
COMMENT ON COLUMN
    "contatos_situacao"."nome" IS 'Situação do contato
    `A` Ativo
    `E` Excluído
    `I` Inativo
    `S` Sem movimentação"'; 