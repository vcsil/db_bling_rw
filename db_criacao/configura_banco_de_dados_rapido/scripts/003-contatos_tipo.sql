CREATE TABLE "contatos_tipo"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(20)         NOT NULL UNIQUE CHECK ("nome" <> ''),
    "sigla" CHAR(1)             NOT NULL UNIQUE CHECK ("sigla" <> '')
);
COMMENT ON COLUMN
    "contatos_tipo"."nome" IS 'Tipo da pessoa
    `J` Jurídica
    `F` Física
    `E` Estrangeira"';
