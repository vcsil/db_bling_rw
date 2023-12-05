CREATE TABLE "tipos_pagamento"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(63)         NOT NULL
);
COMMENT ON COLUMN
    "tipos_pagamento"."nome" IS '`1` Dinheiro
    `2` Cheque
    `3` Cartão de Crédito
    `4` Cartão de Débito
    `5` Crédito Loja
    `10` Vale Alimentação
    `11` Vale Refeição
    `12` Vale Presente
    `13` Vale Combustível
    `14` Duplicata Mercantil
    `15` Boleto Bancário
    `16` Depósito Bancário
    `17` Pagamento Instantâneo (PIX)
    `18` Transferência Bancária, Carteira Digital
    `19` Programa de Fidelidade, Cashback, Crédito Virtual
    `90` Sem pagamento
    `99` Outros';