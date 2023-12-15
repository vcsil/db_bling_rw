CREATE TABLE "modulos"(
    "id_bling"          BIGINT PRIMARY KEY  NOT NULL,
    "nome"              VARCHAR(45)         NOT NULL CHECK ("nome" <> ''),
    "descricao"         VARCHAR(120)        NOT NULL CHECK ("descricao" <> ''),
    "criar_situacoes"   BOOLEAN             NOT NULL
);