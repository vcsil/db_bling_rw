CREATE TABLE "produtos_depositos"(
    "id_bling"              BIGINT PRIMARY KEY  NOT NULL,
    "descricao"             VARCHAR(45)         NOT NULL,
    "situacao"              BOOLEAN             NOT NULL DEFAULT TRUE,
    "padrao"                BOOLEAN             NOT NULL DEFAULT TRUE,
    "desconsiderar_saldo"   BOOLEAN             NOT NULL DEFAULT FALSE
);
COMMENT ON COLUMN
    "produtos_depositos"."situacao" IS '`0` Inativo
    `1` Ativo';