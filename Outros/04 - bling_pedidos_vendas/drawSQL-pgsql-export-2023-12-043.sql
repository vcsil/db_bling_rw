--------------------------------------------------------
--------------------#    VENDAS    #--------------------

CREATE TABLE "modulos"(
    "id_bling"          BIGINT PRIMARY KEY  NOT NULL,
    "nome"              VARCHAR(45)         NOT NULL,
    "descricao"         VARCHAR(120)        NOT NULL,
    "criar_situacoes"   BOOLEAN             NOT NULL
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "situacoes"(
    "id_bling"  BIGINT PRIMARY KEY  NOT NULL,
    "id_modulo" BIGINT              NOT NULL REFERENCES "modulos"("id_bling"),
    "nome"      VARCHAR(45)         NOT NULL,
    "cor"       VARCHAR(7)          NOT NULL
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

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

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "transporte_etiqueta"(
    "id_bling"      BIGINT PRIMARY KEY  NOT NULL,
    "nome"          VARCHAR(63)         NOT NULL,
    "id_endereco"   INTEGER             NOT NULL REFERENCES "enderecos"("id")
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "transporte_volumes"(
    "id_bling"              BIGINT PRIMARY KEY  NOT NULL,
    "servico"               VARCHAR(45)         NOT NULL,
    "codigo_rastreamento"   VARCHAR(45)         NOT NULL
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "transporte"(
    "id"                    SERIAL PRIMARY KEY  NOT NULL,
    "id_frete_por_conta"    INTEGER             NOT NULL REFERENCES "transporte_frete_por_conta_de"("id"),
    "valor_frete"           INTEGER             NOT NULL,
    "quantidade_volumes"    INTEGER,
    "peso_bruto"            INTEGER,
    "prazo_entrega"         INTEGER             NOT NULL,
    "id_contato"            INTEGER             NOT NULL REFERENCES "contatos"("id_bling"),
    "id_etiqueta"           BIGINT              NOT NULL REFERENCES "transporte_etiqueta"("id_bling"),
    "id_volumes"            BIGINT              NOT NULL REFERENCES "transporte_volumes"("id_bling")
);
COMMENT ON COLUMN
    "transporte"."id_contato" IS 'transportador';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "categorias_receitas_despesas"(
    "id_bling"      BIGINT PRIMARY KEY  NOT NULL,
    "nome"          VARCHAR(45)         NOT NULL,
    "tipo"          INTEGER             NOT NULL
);
COMMENT ON COLUMN
    "categorias_receitas_despesas"."tipo" IS '`1` Despesa
    `2` Receita
    `3` Receita e despesa';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "categorias_receitas_despesas_relacao"(
    "id"                    SERIAL PRIMARY KEY  NOT NULL,
    "id_categoria_pai"      BIGINT              NOT NULL REFERENCES "categorias_receitas_despesas"("id_bling"),
    "id_categoria_filho"    BIGINT              NOT NULL UNIQUE REFERENCES "categorias_receitas_despesas"("id_bling")
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "vendas"(
    "id_bling"              BIGINT PRIMARY KEY  NOT NULL,
    "numero"                INTEGER             NOT NULL,
    "numero_loja"           VARCHAR(45),
    "data"                  DATE                NOT NULL DEFAULT 'NOW()',
    "data_saida"            DATE                NOT NULL DEFAULT 'NOW()',
    "data_prevista"         DATE                NOT NULL,
    "id_contato"            BIGINT              NOT NULL REFERENCES "contatos"("id_bling"),
    "id_situacao"           BIGINT              NOT NULL REFERENCES "situacoes"("id_bling"),
    "situacao_valor"        INTEGER             NOT NULL,
    "loja"                  INTEGER             NOT NULL,
    "numero_pedido_compra"  VARCHAR(45),
    "outras_despesas"       INTEGER             NOT NULL,
    "observacoes"           TEXT,
    "observacoes_internas"  TEXT,
    "desconto"              INTEGER             NOT NULL,
    "desconto_unidade"      INTEGER             NOT NULL,
    "id_categoria"          BIGINT              NOT NULL REFERENCES "categorias_receitas_despesas"("id_bling"),
    "id_nota_fiscal"        BIGINT,
    "total_icms"            INTEGER,
    "total_ipi"             INTEGER,
    "id_transporte"         INTEGER             NOT NULL REFERENCES "transporte"("id"),
    "id_vendedor"           BIGINT              NOT NULL REFERENCES "contatos"("id_bling")
);
COMMENT ON COLUMN
    "vendas"."data" IS 'Valor obrigatório caso parâmetro de geração de parcelas seja este';
COMMENT ON COLUMN
    "vendas"."data_saida" IS 'Valor obrigatório caso parâmetro de geração de parcelas seja este';
COMMENT ON COLUMN
    "vendas"."data_prevista" IS 'Valor obrigatório caso parâmetro de geração de parcelas seja este';
COMMENT ON COLUMN
    "vendas"."numero_pedido_compra" IS 'Número da ordem de compra do pedido.';
COMMENT ON COLUMN
    "vendas"."desconto_unidade" IS '0 - Real 1 - Percentual';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "vendas_itens_produtos"(
    "id"            SERIAL PRIMARY KEY  NOT NULL,
    "id_venda"      BIGINT              NOT NULL REFERENCES "vendas"("id_bling"),
    "id_produto"    BIGINT              NOT NULL REFERENCES "produtos"("id_bling"),
    "desconto"      INTEGER             NOT NULL,
    "valor"         INTEGER             NOT NULL,
    "quantidade"    INTEGER             NOT NULL
);
COMMENT ON COLUMN
    "vendas_itens_produtos"."desconto" IS 'Percentual';
COMMENT ON COLUMN
    "vendas_itens_produtos"."valor" IS 'Valor unitário do item. Preço de lista = 4.9 (valor) + 2% (desconto)';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "parcelas"(
    "id_bling"              BIGINT PRIMARY KEY  NOT NULL,
    "id_venda"              BIGINT              NOT NULL REFERENCES "vendas"("id_bling"),
    "data_vencimento"       DATE                NOT NULL DEFAULT 'NOW()',
    "valor"                 INTEGER             NOT NULL,
    "observacoes"           VARCHAR(120)        NOT NULL,
    "id_forma_pagamento"    BIGINT              NOT NULL REFERENCES "formas_pagamento"("id_bling"),
    "id_conta_receber"      BIGINT              NOT NULL REFERENCES "contas_receber"("id_bling")
);
COMMENT ON COLUMN
    "parcelas"."id_bling" IS 'id contas a receber';
