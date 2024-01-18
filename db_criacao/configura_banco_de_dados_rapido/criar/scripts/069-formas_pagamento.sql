CREATE TABLE "formas_pagamento"(
    "id_bling"          BIGINT PRIMARY KEY  NOT NULL,
    "nome"              VARCHAR(45)         NOT NULL  CHECK ("nome" <> ''),
    "id_tipo_pagamento" INTEGER             NOT NULL REFERENCES "tipos_pagamento"("id"),
    "situacao"          BOOLEAN             NOT NULL,
    "fixa"              BOOLEAN             NOT NULL,
    "id_padrao"         INTEGER             NOT NULL REFERENCES "formas_pagamento_padrao"("id"),
    "condicao"          VARCHAR(5)          NOT NULL  CHECK ("condicao" <> ''),
    "id_destino"        INTEGER             NOT NULL REFERENCES "formas_pagamento_destino"("id"),
    "id_finalidade"     INTEGER             NOT NULL REFERENCES "formas_pagamento_finalidade"("id"),
    "taxas_aliquota"    INTEGER             NOT NULL,
    "taxas_valor"       INTEGER             NOT NULL,
    "taxas_prazo"       INTEGER             NOT NULL,
);
COMMENT ON COLUMN
    "formas_pagamento"."situacao" IS '`0` Inativa
    `1` Ativa';
COMMENT ON COLUMN
    "formas_pagamento"."id_padrao" IS '`0` Não
    `1` Padrão
    `2` Padrão devolução"';