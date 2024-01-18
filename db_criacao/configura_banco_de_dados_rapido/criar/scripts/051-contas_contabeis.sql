CREATE TABLE "contas_contabeis"(
    "id_bling"  BIGINT PRIMARY KEY  NOT NULL,
    "nome"      VARCHAR(45)         NOT NULL  CHECK ("descricao" <> '')
);
