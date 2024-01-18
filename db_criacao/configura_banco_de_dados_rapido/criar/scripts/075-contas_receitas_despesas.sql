CREATE TABLE "contas_receitas_despesas"(
    "id_bling"                      BIGINT PRIMARY KEY  NOT NULL,
    "id_situacao"                   INTEGER             REFERENCES "contas_situacao"("id"),
    "vencimento"                    DATE                NOT NULL,
    "valor"                         INTEGER             NOT NULL,
    "id_contato"                    BIGINT              NOT NULL REFERENCES "contatos"("id_bling"),
    "id_forma_pagamento"            BIGINT              NOT NULL REFERENCES "formas_pagamento"("id_bling"),
    "saldo"                         INTEGER             NOT NULL,
    "data_emissao"                  DATE                NOT NULL DEFAULT NOW(),
    "vencimento_original"           DATE                NOT NULL DEFAULT NOW(),
    "numero_documento"              VARCHAR(63)         CHECK ("numero_documento" <> ''),
    "competencia"                   DATE                NOT NULL,
    "historico"                     TEXT                NOT NULL,
    "numero_banco"                  VARCHAR(63),
    "id_portador"                   BIGINT              REFERENCES "contas_contabeis"("id_bling"),
    "id_categoria_receita_despesa"  BIGINT              NOT NULL REFERENCES "categorias_receitas_despesas"("id_bling"),
    "id_vendedor"                   BIGINT              REFERENCES "vendedores"("id_bling"),
    "id_bordero"                    BIGINT,
    "id_tipo_ocorrencia"            INTEGER             NOT NULL REFERENCES "contas_tipo_ocorrencia"("id"),
    "considerar_dias_uteis"         BOOLEAN,
    "dia_vencimento"                DATE                DEFAULT NOW(),
    "numero_parcelas"               INTEGER,
    "data_limite"                   DATE                DEFAULT NOW()

);
COMMENT ON COLUMN
    "contas_receber"."saldo" IS 'É calculado subtraindo os valores dos recebimentos do valor da conta';
COMMENT ON COLUMN
    "contas_receber"."numero_documento" IS '"Número para controle interno da empresa"';
COMMENT ON COLUMN
    "contas_receber"."historico" IS '"Descriçao da conta para controle interno da empresa"';
COMMENT ON COLUMN
    "contas_receber"."numero_banco" IS '"Adicionado automaticamente com o número preenchido no cadastro do banco"';
COMMENT ON COLUMN
    "contas_receber"."tipo_ocorrencia" IS '`1` Única `2` Parcelada `3` Mensal `4` Bimestral `5` Trimestral `6` Semestral `7` Anual `8` Quinzenal `9` Semanal';
