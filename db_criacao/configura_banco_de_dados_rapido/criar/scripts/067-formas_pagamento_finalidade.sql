CREATE TABLE "formas_pagamento_finalidade"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(26)         NOT NULL  CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "formas_pagamento_finalidade"."nome" IS '`1` Pagamentos
    `2` Recebimentos
    `3` Pagamentos e Recebimentos';