CREATE TABLE "endereco_paises"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(63)         NOT NULL    UNIQUE CHECK ("nome" <> '')
);
COMMENT ON TABLE
    "endereco_paises" IS 'Bloqueio para repetir país';
