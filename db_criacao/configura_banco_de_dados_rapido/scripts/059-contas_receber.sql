CREATE TABLE "contas_receber"(
    "id_bling"              BIGINT PRIMARY KEY  NOT NULL,
    "id_situacao"           INTEGER             NOT NULL REFERENCES "contas_receber_situacao"("id"),
    "vencimento"            DATE                NOT NULL,
    "valor"                 INTEGER             NOT NULL,
    "id_contato"            BIGINT              NOT NULL REFERENCES "contatos"("id_bling"),
    "id_forma_pagamento"    BIGINT              NOT NULL REFERENCES "formas_pagamento"("id_bling"),
    "saldo"                 INTEGER             NOT NULL,
    "data_emissao"          DATE                NOT NULL,
    "vencimento_original"   DATE                NOT NULL,
    "numero_documento"      VARCHAR(63)         NOT NULL CHECK ("numero_documento" <> ''),
    "competencia"           DATE                NOT NULL,
    "historico"             TEXT                NOT NULL,
    "numero_banco"          VARCHAR(63)         NOT NULL CHECK ("numero_banco" <> ''),
    "id_portador"           BIGINT              NOT NULL REFERENCES "contas_contabeis"("id")
);
COMMENT ON COLUMN
    "contas_receber"."saldo" IS 'É calculado subtraindo os valores dos recebimentos do valor da conta';
COMMENT ON COLUMN
    "contas_receber"."numero_documento" IS '"Número para controle interno da empresa"';
COMMENT ON COLUMN
    "contas_receber"."historico" IS '"Descriçao da conta para controle interno da empresa"';
COMMENT ON COLUMN
    "contas_receber"."numero_banco" IS '"Adicionado automaticamente com o número preenchido no cadastro do banco"';