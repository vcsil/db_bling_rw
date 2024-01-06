CREATE TABLE "contas_contabeis"(
    "id"        BIGINT PRIMARY KEY  NOT NULL,
    "descricao" VARCHAR(45)         NOT NULL  CHECK ("descricao" <> '')
);