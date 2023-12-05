CREATE TABLE "transporte_frete_por_conta_de"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(63)         NOT NULL
);
COMMENT ON COLUMN
    "transporte_frete_por_conta_de"."nome" IS '`0` Contratação do Frete por conta do Remetente (CIF)
    `1` Contratação do Frete por conta do Destinatário (FOB)
    `2` Contratação do Frete por conta de Terceiros
    `3` Transporte Próprio por conta do Remetente
    `4` Transporte Próprio por conta do Destinatário
    `9` Sem Ocorrência de Transporte."';