CREATE TABLE "vendas"(
    "id_bling"                      BIGINT PRIMARY KEY  NOT NULL,
    "numero"                        INTEGER             NOT NULL,
    "numero_loja"                   VARCHAR(45),
    "data"                          TIMESTAMPTZ         NOT NULL DEFAULT current_timestamp,
    "data_saida"                    DATE                DEFAULT NOW(),
    "data_prevista"                 DATE,
    "id_contato"                    BIGINT              NOT NULL REFERENCES "contatos"("id_bling"),
    "id_situacao"                   BIGINT              NOT NULL REFERENCES "situacoes"("id_bling"),
    "situacao_valor"                INTEGER             NOT NULL,
    "id_loja"                       INTEGER             NOT NULL,
    "numero_pedido_compra"          VARCHAR(45),
    "outras_despesas"               INTEGER             NOT NULL,
    "observacoes"                   TEXT,
    "observacoes_internas"          TEXT,
    "desconto"                      INTEGER             NOT NULL,
    "desconto_unidade"              VARCHAR(12)             NOT NULL,
    "id_categoria"                  BIGINT              REFERENCES "categorias_receitas_despesas"("id_bling"),
    "id_nota_fiscal"                BIGINT,
    "total_icms"                    INTEGER,
    "total_ipi"                     INTEGER,
    "id_vendedor"                   BIGINT              REFERENCES "vendedores"("id_bling"),
    "transporte_id_frete_por_conta" INTEGER             NOT NULL REFERENCES "transporte_frete_por_conta_de"("id"),
    "transporte_valor_frete"        INTEGER             NOT NULL,
    "transporte_quantidade_volumes" INTEGER,
    "transporte_peso_bruto"         INTEGER,
    "transporte_prazo_entrega"      INTEGER,
    "transporte_id_contato"         INTEGER             REFERENCES "contatos"("id_bling"),
    "transporte_id_etiqueta"        BIGINT              REFERENCES "transporte_etiqueta"("id")
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
COMMENT ON COLUMN
    "vendas"."transporte_id_contato" IS 'transportador';
