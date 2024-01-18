CREATE TABLE contas_tipo_ocorrencia (
        "id"      SERIAL PRIMARY KEY  NOT NULL
    ,   "nome"    VARCHAR(12)         NOT NULL  CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "contas_tipo_ocorrencia"."nome" IS '`1` Única 
`2` Parcelada 
`3` Mensal
`4` Bimestral
`5` Trimestral
`6` Semestral
`7` Anual
`8` Quinzenal
`9` Semanal';