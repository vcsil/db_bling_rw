CREATE TABLE "formas_pagamento_padrao"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(16)         NOT NULL  CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "formas_pagamento_padrao"."nome" IS '`1` Pagamentos
    `2` Recebimentos
    `3` Pagamentos e Recebimentos';