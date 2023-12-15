CREATE TABLE "transporte_etiqueta"(
    "id_bling"      BIGINT PRIMARY KEY  NOT NULL,
    "nome"          VARCHAR(63)         NOT NULL CHECK ("nome" <> ''),
    "id_endereco"   INTEGER             NOT NULL REFERENCES "enderecos"("id")
);