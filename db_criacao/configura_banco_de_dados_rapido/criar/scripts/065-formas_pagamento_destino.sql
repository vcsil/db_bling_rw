CREATE TABLE "formas_pagamento_destino"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(22)         NOT NULL  CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "formas_pagamento_destino"."nome" IS '`1` Conta a receber/pagar
    `2` Ficha financeira
    `3` Caixa e bancos';