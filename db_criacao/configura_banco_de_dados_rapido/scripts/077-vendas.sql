CREATE TABLE "vendas"(
    "id_bling"              BIGINT PRIMARY KEY  NOT NULL,
    "numero"                INTEGER             NOT NULL,
    "numero_loja"           VARCHAR(45),
    "data"                  TIMESTAMPTZ         NOT NULL DEFAULT current_timestamp,
    "data_saida"            DATE                NOT NULL DEFAULT NOW(),
    "data_prevista"         DATE                NOT NULL,
    "id_contato"            BIGINT              NOT NULL REFERENCES "contatos"("id_bling"),
    "id_situacao"           BIGINT              NOT NULL REFERENCES "situacoes"("id_bling"),
    "situacao_valor"        INTEGER             NOT NULL,
    "loja"                  INTEGER             NOT NULL,
    "numero_pedido_compra"  VARCHAR(45),
    "outras_despesas"       INTEGER             NOT NULL,
    "observacoes"           TEXT,
    "observacoes_internas"  TEXT,
    "desconto"              INTEGER             NOT NULL,
    "desconto_unidade"      INTEGER             NOT NULL,
    "id_categoria"          BIGINT              NOT NULL REFERENCES "categorias_receitas_despesas"("id_bling"),
    "id_nota_fiscal"        BIGINT,
    "total_icms"            INTEGER,
    "total_ipi"             INTEGER,
    "id_transporte"         INTEGER             NOT NULL REFERENCES "transporte"("id"),
    "id_vendedor"           BIGINT              NOT NULL REFERENCES "contatos"("id_bling")
);
COMMENT ON COLUMN
    "vendas"."data" IS 'Valor obrigatório caso parâmetro de geração de parcelas seja este';
COMMENT ON COLUMN
    "vendas"."data_saida" IS 'Valor obrigatório caso parâmetro de geração de parcelas seja este';
COMMENT ON COLUMN
    "vendas"."data_prevista" IS 'Valor obrigatório caso parâmetro de geração de parcelas seja este';
COMMENT ON COLUMN
    "vendas"."numero_pedido_compra" IS 'Número da ordem de compra do pedido.';
COMMENT ON COLUMN
    "vendas"."desconto_unidade" IS '0 - Real 1 - Percentual';
