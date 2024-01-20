--------------------------------------------------------
-----------------#   CONTAS RECEBER   #-----------------

CREATE TABLE "contas_contabeis"(
    "id_bling"  BIGINT PRIMARY KEY  NOT NULL,
    "nome"      VARCHAR(45)         NOT NULL  CHECK ("descricao" <> '')
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "categorias_receitas_despesas_tipo"(
    "id"    BIGINT PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(18)         NOT NULL CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "categorias_receitas_despesas_tipo"."nome" IS '`1` Despesa
    `2` Receita
    `3` Receita e despesa';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "categorias_receitas_despesas"(
    "id_bling"      BIGINT PRIMARY KEY  NOT NULL,
    "nome"          VARCHAR(45)         NOT NULL CHECK ("nome" <> ''),
    "id_tipo"       INTEGER          	NOT NULL REFERENCES "categorias_receitas_despesas_tipo"("id"),
    "situacao"	    BOOLEAN		NOT NULL
);
COMMENT ON COLUMN
    "categorias_receitas_despesas"."id_tipo" IS '`1` Despesa
    `2` Receita
    `3` Receita e despesa';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "categorias_receitas_despesas_relacao"(
    "id"                    SERIAL PRIMARY KEY  NOT NULL,
    "id_categoria_pai"      BIGINT              NOT NULL REFERENCES "categorias_receitas_despesas"("id_bling"),
    "id_categoria_filho"    BIGINT              NOT NULL UNIQUE REFERENCES "categorias_receitas_despesas"("id_bling")
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contas_situacao"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(45)         NOT NULL  CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "contas_situacao"."nome" IS '`1` Em aberto
    `2` Recebido
    `3` Parcialmente recebido
    `4` Devolvido
    `5` Cancelado';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "tipos_pagamento"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(63)         NOT NULL  CHECK ("nome" <> '')
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

CREATE TABLE "formas_pagamento_padrao"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(16)         NOT NULL  CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "formas_pagamento_padrao"."nome" IS '`1` Pagamentos
    `2` Recebimentos
    `3` Pagamentos e Recebimentos';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "formas_pagamento_destino"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(22)         NOT NULL  CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "formas_pagamento_destino"."nome" IS '`1` Conta a receber/pagar
    `2` Ficha financeira
    `3` Caixa e bancos';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "formas_pagamento_finalidade"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(26)         NOT NULL  CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "formas_pagamento_finalidade"."nome" IS '`1` Pagamentos
    `2` Recebimentos
    `3` Pagamentos e Recebimentos';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

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
    "taxas_prazo"       INTEGER             NOT NULL
);
COMMENT ON COLUMN
    "formas_pagamento"."situacao" IS '`0` Inativa
    `1` Ativa';
COMMENT ON COLUMN
    "formas_pagamento"."id_padrao" IS '`0` Não
    `1` Padrão
    `2` Padrão devolução"';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

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

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "vendedores"(
        "id_bling"                  BIGINT PRIMARY KEY  NOT NULL
    ,   "desconto_limite"           INTEGER             NOT NULL
    ,   "id_loja"                   INTEGER             NOT NULL
    ,   "comissoes_desconto_maximo" INTEGER             NOT NULL
    ,   "comissoes_aliquota"        INTEGER             NOT NULL
    ,   "id_contato"                BIGINT              NOT NULL REFERENCES "contatos"("id_bling")
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contas_receitas_despesas"(
    "id_bling"                      BIGINT PRIMARY KEY  NOT NULL,
    "id_situacao"                   INTEGER             REFERENCES "contas_situacao"("id"),
    "vencimento"                    DATE                NOT NULL,
    "valor"                         INTEGER             NOT NULL,
    "id_contato"                    BIGINT              NOT NULL REFERENCES "contatos"("id_bling"),
    "id_forma_pagamento"            BIGINT              NOT NULL REFERENCES "formas_pagamento"("id_bling"),
    "saldo"                         INTEGER             NOT NULL,
    "data_emissao"                  DATE                NOT NULL DEFAULT NOW(),
    "vencimento_original"           DATE                NOT NULL DEFAULT NOW(),
    "numero_documento"              VARCHAR(63)         CHECK ("numero_documento" <> ''),
    "competencia"                   DATE                NOT NULL,
    "historico"                     TEXT                NOT NULL,
    "numero_banco"                  VARCHAR(63),
    "id_portador"                   BIGINT              REFERENCES "contas_contabeis"("id_bling"),
    "id_categoria_receita_despesa"  BIGINT              NOT NULL REFERENCES "categorias_receitas_despesas"("id_bling"),
    "id_vendedor"                   BIGINT              REFERENCES "vendedores"("id_bling"),
    "id_bordero"                    BIGINT,
    "id_tipo_ocorrencia"            INTEGER             NOT NULL REFERENCES "contas_tipo_ocorrencia"("id"),
    "considerar_dias_uteis"         BOOLEAN,
    "dia_vencimento"                DATE                DEFAULT NOW(),
    "numero_parcelas"               INTEGER,
    "data_limite"                   DATE                DEFAULT NOW()

);
COMMENT ON COLUMN
    "contas_receber"."saldo" IS 'É calculado subtraindo os valores dos recebimentos do valor da conta';
COMMENT ON COLUMN
    "contas_receber"."numero_documento" IS '"Número para controle interno da empresa"';
COMMENT ON COLUMN
    "contas_receber"."historico" IS '"Descriçao da conta para controle interno da empresa"';
COMMENT ON COLUMN
    "contas_receber"."numero_banco" IS '"Adicionado automaticamente com o número preenchido no cadastro do banco"';
COMMENT ON COLUMN
    "contas_receber"."tipo_ocorrencia" IS '`1` Única `2` Parcelada `3` Mensal `4` Bimestral `5` Trimestral `6` Semestral `7` Anual `8` Quinzenal `9` Semanal';

