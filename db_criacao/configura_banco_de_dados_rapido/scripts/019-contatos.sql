CREATE TABLE "contatos"(
    "id_bling"                          BIGINT PRIMARY KEY  NOT NULL,
    "nome"                              VARCHAR(120)        NOT NULL CHECK ("nome" <> ''),
    "sobrenome"                         VARCHAR(255)        NOT NULL,
    "codigo"                            VARCHAR(45),
    "id_situacao_contato"               INTEGER             NOT NULL REFERENCES "contatos_situacao"("id"),
    "numero_documento"                  VARCHAR(14),
    "telefone"                          VARCHAR(15),
    "celular"                           VARCHAR(15),
    "fantasia"                          VARCHAR(63),
    "id_tipo_contato"                   INTEGER             NOT NULL  REFERENCES "contatos_tipo"("id"),
    "id_indicador_inscricao_estadual"   INTEGER             NOT NULL  REFERENCES "contatos_indicador_inscricao_estadual"("id"),
    "inscricao_estadual"                VARCHAR(12),
    "rg"                                VARCHAR(10),
    "orgao_emissor"                     VARCHAR(55),
    "email"                             VARCHAR(255),
    "data_nascimento"                   DATE,
    "sexo"                              INTEGER             NOT NULL CHECK (sexo IN (1, 2, 3)),
    "id_classificacao_contato"          BIGINT                       REFERENCES "contatos_classificacao"("id_bling"),
);
COMMENT ON COLUMN
    "contatos"."numero_documento" IS 'CPF ou CNPJ do contato';
COMMENT ON COLUMN
    "contatos"."telefone" IS '+5511998765432';
COMMENT ON COLUMN
    "contatos"."celular" IS '+5511998765432';
COMMENT ON COLUMN
    "contatos"."sexo" IS '1 Masculino
    2 Feminino
    3 Outro';
