CREATE TABLE "transporte"(
    "id"                    SERIAL PRIMARY KEY  NOT NULL,
    "id_frete_por_conta"    INTEGER             NOT NULL REFERENCES "transporte_frete_por_conta_de"("id"),
    "valor_frete"           INTEGER             NOT NULL,
    "quantidade_volumes"    INTEGER,
    "peso_bruto"            INTEGER,
    "prazo_entrega"         INTEGER             NOT NULL,
    "id_contato"            INTEGER             NOT NULL REFERENCES "contatos"("id_bling"),
    "id_etiqueta"           BIGINT              NOT NULL REFERENCES "transporte_etiqueta"("id_bling"),
    "id_volumes"            BIGINT              NOT NULL REFERENCES "transporte_volumes"("id_bling")
);
COMMENT ON COLUMN
    "transporte"."id_contato" IS 'transportador';