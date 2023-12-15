CREATE TABLE "transporte_volumes"(
    "id_bling"              BIGINT PRIMARY KEY  NOT NULL,
    "servico"               VARCHAR(45)         NOT NULL CHECK ("servico" <> ''),
    "codigo_rastreamento"   VARCHAR(45)         NOT NULL CHECK ("codigo_rastreamento" <> '')
);