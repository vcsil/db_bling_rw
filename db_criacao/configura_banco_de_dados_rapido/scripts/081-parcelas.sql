CREATE TABLE "parcelas"(
    "id_bling"              BIGINT PRIMARY KEY  NOT NULL,
    "id_venda"              BIGINT              NOT NULL REFERENCES "vendas"("id_bling"),
    "data_vencimento"       DATE                NOT NULL DEFAULT 'NOW()',
    "valor"                 INTEGER             NOT NULL,
    "observacoes"           VARCHAR(120)        NOT NULL,
    "id_forma_pagamento"    BIGINT              NOT NULL REFERENCES "formas_pagamento"("id_bling"),
    "id_conta_receber"      BIGINT              NOT NULL REFERENCES "contas_receber"("id_bling")
);
COMMENT ON COLUMN
    "parcelas"."id_bling" IS 'id contas a receber';