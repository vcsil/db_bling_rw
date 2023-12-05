--------------------------------------------------------
-----------------#   CONTAS RECEBER   #-----------------

CREATE TABLE "contas_contabeis"(
    "id"        BIGINT PRIMARY KEY  NOT NULL,
    "descricao" VARCHAR(45)         NOT NULL
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contas_receber_situacao"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(45)         NOT NULL
);
COMMENT ON COLUMN
    "contas_receber_situacao"."nome" IS '`1` Em aberto
    `2` Recebido
    `3` Parcialmente recebido
    `4` Devolvido
    `5` Cancelado';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

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

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "formas_pagamento"(
    "id_bling"          BIGINT PRIMARY KEY  NOT NULL,
    "nome"              VARCHAR(45)         NOT NULL,
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

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contas_receber"(
    "id_bling"              BIGINT PRIMARY KEY  NOT NULL,
    "id_situacao"           INTEGER             NOT NULL REFERENCES "contas_receber_situacao"("id"),
    "vencimento"            DATE                NOT NULL,
    "valor"                 INTEGER             NOT NULL,
    "id_contato"            BIGINT              NOT NULL REFERENCES "contatos"("id_bling"),
    "id_forma_pagamento"    BIGINT              NOT NULL REFERENCES "formas_pagamento"("id_bling"),
    "saldo"                 INTEGER             NOT NULL,
    "data_emissao"          DATE                NOT NULL,
    "vencimento_original"   DATE                NOT NULL,
    "numero_documento"      VARCHAR(63)         NOT NULL,
    "competencia"           DATE                NOT NULL,
    "historico"             TEXT                NOT NULL,
    "numero_banco"          VARCHAR(63)         NOT NULL,
    "id_portador"           BIGINT              NOT NULL REFERENCES "contas_contabeis"("id")
);
COMMENT ON COLUMN
    "contas_receber"."saldo" IS 'É calculado subtraindo os valores dos recebimentos do valor da conta';
COMMENT ON COLUMN
    "contas_receber"."numero_documento" IS '"Número para controle interno da empresa"';
COMMENT ON COLUMN
    "contas_receber"."historico" IS '"Descriçao da conta para controle interno da empresa"';
COMMENT ON COLUMN
    "contas_receber"."numero_banco" IS '"Adicionado automaticamente com o número preenchido no cadastro do banco"';
