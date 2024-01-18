CREATE TABLE "situacoes"(
    "id_bling"  BIGINT PRIMARY KEY  NOT NULL,
    "id_modulo" BIGINT              NOT NULL REFERENCES "modulos"("id_bling"),
    "nome"      VARCHAR(45)         NOT NULL CHECK ("nome" <> ''),
    "cor"       VARCHAR(7)          NOT NULL CHECK ("cor" <> '')
);