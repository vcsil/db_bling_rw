CREATE TABLE "transporte_volumes"(
    "id_bling"              BIGINT PRIMARY KEY  NOT NULL,
    "id_venda"         	    BIGINT              NOT NULL REFERENCES "vendas"("id_bling"),
    "servico"               VARCHAR(45),
    "codigo_rastreamento"   VARCHAR(45)
);
