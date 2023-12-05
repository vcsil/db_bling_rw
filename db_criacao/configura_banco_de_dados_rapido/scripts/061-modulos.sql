CREATE TABLE "modulos"(
    "id_bling"          BIGINT PRIMARY KEY  NOT NULL,
    "nome"              VARCHAR(45)         NOT NULL,
    "descricao"         VARCHAR(120)        NOT NULL,
    "criar_situacoes"   BOOLEAN             NOT NULL
);