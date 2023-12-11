CREATE TABLE "contatos_indicador_inscricao_estadual"(
    "id"    INTEGER PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(63)         NOT NULL UNIQUE
);
COMMENT ON COLUMN
    "contatos_indicador_inscricao_estadual"."nome" IS 'Indicador de inscrição estadual
    `1` Contribuinte ICMS 
    `2` Contribuinte isento de Inscrição no cadastro de Contribuintes
    `9` Não Contribuinte"';
