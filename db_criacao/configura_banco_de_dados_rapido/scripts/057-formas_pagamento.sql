CREATE TABLE "formas_pagamento"(
    "id_bling"          BIGINT PRIMARY KEY  NOT NULL,
    "nome"              VARCHAR(45)         NOT NULL  CHECK ("nome" <> ''),
    "id_tipo_pagamento" INTEGER             NOT NULL REFERENCES "tipos_pagamento"("id"),
    "situacao"          BOOLEAN             NOT NULL,
    "fixa"              BOOLEAN             NOT NULL,
    "padrão"            INTEGER             NOT NULL
);
COMMENT ON COLUMN
    "formas_pagamento"."situacao" IS '`0` Inativa
    `1` Ativa';
COMMENT ON COLUMN
    "formas_pagamento"."padrão" IS '`0` Não
    `1` Padrão
    `2` Padrão devolução"';