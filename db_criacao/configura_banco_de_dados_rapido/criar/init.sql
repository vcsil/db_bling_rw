CREATE TABLE "contatos_situacao"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(20)         NOT NULL UNIQUE CHECK ("nome" <> ''),
    "sigla" CHAR(1)             NOT NULL UNIQUE CHECK ("sigla" <> '')
);
COMMENT ON COLUMN
    "contatos_situacao"."nome" IS 'Situação do contato
    `A` Ativo
    `E` Excluído
    `I` Inativo
    `S` Sem movimentação"'; 

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contatos_tipo"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(20)         NOT NULL UNIQUE CHECK ("nome" <> ''),
    "sigla" CHAR(1)             NOT NULL UNIQUE CHECK ("sigla" <> '')
);
COMMENT ON COLUMN
    "contatos_tipo"."nome" IS 'Tipo da pessoa
    `J` Jurídica
    `F` Física
    `E` Estrangeira"';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contatos_indicador_inscricao_estadual"(
    "id"    INTEGER PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(63)         NOT NULL UNIQUE CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "contatos_indicador_inscricao_estadual"."nome" IS 'Indicador de inscrição estadual
    `1` Contribuinte ICMS 
    `2` Contribuinte isento de Inscrição no cadastro de Contribuintes
    `9` Não Contribuinte"';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contatos_classificacao"(
    "id_bling"  BIGINT PRIMARY KEY  NOT NULL,
    "nome"      VARCHAR(63)         NOT NULL UNIQUE CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "contatos_classificacao"."nome" IS 'Fornecedor etc';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "endereco_paises"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(63)         NOT NULL    UNIQUE CHECK ("nome" <> '')
);
COMMENT ON TABLE
    "endereco_paises" IS 'Bloqueio para repetir país';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "endereco_unidade_federativa"(
    "id"        SERIAL PRIMARY KEY  NOT NULL,
    "nome"      VARCHAR(63),	    --NOT NULL CHECK ("nome" <> ''),
    "id_pais"   INTEGER             NOT NULL REFERENCES "endereco_paises"("id")
    
    , CONSTRAINT uq_uf_idpais UNIQUE ("nome", "id_pais")
);
COMMENT ON TABLE
    "endereco_unidade_federativa" IS 'Bloqueio para repetir a mesma UF em um mesmo País';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "endereco_municipios"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(63),
    "id_uf" INTEGER             NOT NULL REFERENCES "endereco_unidade_federativa"("id")
    
    , CONSTRAINT uq_municipio_iduf UNIQUE ("nome", "id_uf")
);
COMMENT ON TABLE
    "endereco_municipios" IS 'Bloqueio para repetir o mesmo município em um mesmo UF';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "endereco_bairros"(
    "id"            SERIAL PRIMARY KEY  NOT NULL,
    "nome"          VARCHAR(63),
    "id_municipio"  INTEGER             NOT NULL REFERENCES "endereco_municipios"("id")
    
    , CONSTRAINT uq_bairro_idmunicipio UNIQUE ("nome", "id_municipio")
);
COMMENT ON TABLE
    "endereco_bairros" IS 'Bloqueio para repetir o mesmo bairro em um mesmo município';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "enderecos"(
    "id"            SERIAL PRIMARY KEY  NOT NULL,
    "endereco"      VARCHAR(127),
    "cep"           VARCHAR(8),
    "id_bairro"     INTEGER             NOT NULL REFERENCES "endereco_bairros"("id"),
    "id_municipio"  INTEGER             NOT NULL REFERENCES "endereco_municipios"("id"),
    "id_uf"         INTEGER             NOT NULL REFERENCES "endereco_unidade_federativa"("id"),
    "id_pais"       INTEGER             NOT NULL REFERENCES "endereco_paises"("id"),
    "numero"        VARCHAR(10),
    "complemento"   VARCHAR(127)
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contatos"(
    "id_bling"                          BIGINT PRIMARY KEY  NOT NULL,
    "nome"                              VARCHAR(120)        NOT NULL CHECK ("nome" <> ''),
    "sobrenome"                         VARCHAR(255)        NOT NULL,
    "codigo"                            VARCHAR(45),
    "id_situacao_contato"               INTEGER             NOT NULL REFERENCES "contatos_situacao"("id"),
    "numero_documento"                  VARCHAR(14),
    "telefone"                          VARCHAR(15),
    "celular"                           VARCHAR(15),
    "fantasia"                          VARCHAR(63),
    "id_tipo_contato"                   INTEGER             NOT NULL  REFERENCES "contatos_tipo"("id"),
    "id_indicador_inscricao_estadual"   INTEGER             NOT NULL  REFERENCES "contatos_indicador_inscricao_estadual"("id"),
    "inscricao_estadual"                VARCHAR(13),
    "rg"                                VARCHAR(10),
    "orgao_emissor"                     VARCHAR(55),
    "email"                             VARCHAR(255),
    "data_nascimento"                   DATE,
    "sexo"                              INTEGER             NOT NULL CHECK (sexo IN (1, 2, 3)) DEFAULT 2,
    "id_classificacao_contato"          BIGINT                       REFERENCES "contatos_classificacao"("id_bling"),
    "cliente_desde"			TIMESTAMPTZ	    NOT NULL DEFAULT current_timestamp,
    "alterado_em"			TIMESTAMPTZ	    DEFAULT NULL
);
COMMENT ON COLUMN
    "contatos"."numero_documento" IS 'CPF ou CNPJ do contato';
COMMENT ON COLUMN
    "contatos"."telefone" IS '+5511998765432';
COMMENT ON COLUMN
    "contatos"."celular" IS '+5511998765432';
COMMENT ON COLUMN
    "contatos"."sexo" IS '1 Masculino
    2 Feminino
    3 Outro';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contatos_enderecos"(
    "id"            SERIAL PRIMARY KEY  NOT NULL,
    "id_contato"    BIGINT              NOT NULL REFERENCES "contatos"("id_bling"),
    "id_endereco"   INTEGER             NOT NULL REFERENCES "enderecos"("id"),
    "tipo_endereco" SMALLINT            NOT NULL
);
COMMENT ON TABLE
    "contatos_enderecos" IS '`0`: Geral \n `1`: Cobrança';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_tipos"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(20)         NOT NULL UNIQUE CHECK ("nome" <> ''),
    "sigla" CHAR(1)             NOT NULL UNIQUE CHECK ("sigla" <> '')
);
COMMENT ON COLUMN
    "produtos_tipos"."nome" IS 'Tipo do produto
    `S` Serviço
    `P` Produto
    `N` Serviço 06 21 22';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_formatos"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(15)         NOT NULL UNIQUE CHECK ("nome" <> ''),
    "sigla" CHAR(1)             NOT NULL UNIQUE CHECK ("sigla" <> '')
);
COMMENT ON COLUMN
    "produtos_formatos"."nome" IS 'Formato do produto
    `S` Simples
    `V` Com variações
    `E` Com composição';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_tipo_producao"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(10)         NOT NULL UNIQUE CHECK ("nome" <> ''),
    "sigla" CHAR(1)             NOT NULL UNIQUE CHECK ("sigla" <> '')
);
COMMENT ON COLUMN
    "produtos_tipo_producao"."nome" IS 'Tipo da produção
    `P` Própria
    `T` Terceiros"';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_condicao"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(17)         NOT NULL CHECK ("nome" <> '')
);
COMMENT ON COLUMN
    "produtos_condicao"."nome" IS 'Condição do produto
    `0` Não especificado
    `1` Novo
    `2` Usado"';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_categorias"(
    "id_bling"  BIGINT PRIMARY KEY  NOT NULL,
    "nome"      VARCHAR(120)        NOT NULL CHECK ("nome" <> '')
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_categorias_relacao"(
    "id"                    SERIAL PRIMARY KEY  NOT NULL,
    "id_categoria_pai"      BIGINT              NOT NULL REFERENCES "produtos_categorias"("id_bling"),
    "id_categoria_filho"    BIGINT              NOT NULL UNIQUE REFERENCES "produtos_categorias"("id_bling")
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "dimensoes"(
    "id"                SERIAL PRIMARY KEY  NOT NULL,
    "largura"           INTEGER             NOT NULL,
    "altura"            INTEGER             NOT NULL,
    "profundidade"      INTEGER             NOT NULL,
    "unidade_medida"    INTEGER             NOT NULL
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_midias"(
    "id"    		    SERIAL PRIMARY KEY  NOT NULL,
    "tipo"  		    BOOLEAN             NOT NULL,
    "url"   		    TEXT                NOT NULL,
    "url_miniatura"     TEXT,
    "diretorio_local"   TEXT                DEFAULT NULL,
    "validade" 		    TIMESTAMPTZ	        NOT NULL,
    "criado_em"	        TIMESTAMPTZ	        NOT NULL DEFAULT current_timestamp
);
COMMENT ON COLUMN
    "produtos_midias"."tipo" IS 'True: Foto
    False: Video';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos"(
    "id_bling"                  BIGINT PRIMARY KEY  NOT NULL,
    "nome"                      VARCHAR(120)        NOT NULL CHECK ("nome" <> ''), --UNIQUE
    "codigo"                    VARCHAR(120)        NOT NULL CHECK ("codigo" <> ''),
    "preco"                     INTEGER             NOT NULL,
    "id_tipo_produto"           INTEGER             NOT NULL DEFAULT 2 REFERENCES "produtos_tipos"("id"),
    "situacao_produto"          VARCHAR(10)         NOT NULL DEFAULT 'Ativo',
    "id_formato_produto"        INTEGER             NOT NULL REFERENCES "produtos_formatos"("id"),
    "id_produto_pai"		BIGINT		    DEFAULT NULL REFERENCES "produtos"("id_bling"),
    "descricao_curta"           TEXT,
    "data_validade"             DATE,
    "unidade"                   VARCHAR(6)          DEFAULT 'UN'  CHECK ("unidade" <> ''),
    "peso_liquido"              INTEGER             NOT NULL DEFAULT 1,
    "peso_bruto"                INTEGER             NOT NULL DEFAULT 1,
    "volumes"                   INTEGER             NOT NULL DEFAULT 1,
    "itens_por_caixa"           INTEGER             NOT NULL DEFAULT 1,
    "gtin"                      VARCHAR(14),
    "gtin_embalagem"            VARCHAR(13),
    "id_tipo_producao"          INTEGER             DEFAULT 1 REFERENCES "produtos_tipo_producao"("id"),
    "id_condicao_producao"      INTEGER             NOT NULL REFERENCES "produtos_condicao"("id"),
    "frete_gratis"              BOOLEAN             NOT NULL DEFAULT FALSE,
    "marca"                     VARCHAR(45)         NOT NULL DEFAULT 'RW'  CHECK ("marca" <> ''),
    "descricao_complementar"    TEXT,
    "link_externo"              TEXT,
    "observacoes"               TEXT,
    "id_categoria_produto"      BIGINT              NOT NULL REFERENCES "produtos_categorias"("id_bling"),
    "estoque_minimo"            INTEGER             NOT NULL DEFAULT 0,
    "estoque_maximo"            INTEGER             NOT NULL DEFAULT 0,
    "estoque_crossdocking"      INTEGER             NOT NULL DEFAULT 0,
    "estoque_localizacao"       VARCHAR(45),
    "id_dimensoes"              INTEGER             NOT NULL REFERENCES "dimensoes"("id"),
    "ncm"           		VARCHAR(10)         DEFAULT '7113.20.00' CHECK ("ncm" <> ''),
    "cest"          		VARCHAR(9)          DEFAULT '28.058.00' CHECK ("cest" <> ''),
    "id_midia_principal"        INTEGER             REFERENCES "produtos_midias"("id"),
    "criado_em"			TIMESTAMPTZ	    NOT NULL DEFAULT current_timestamp,
    "alterado_em"		TIMESTAMPTZ	    DEFAULT NULL

    --, CONSTRAINT uq_nome_codigo UNIQUE ("nome", "codigo", situacao_produto)
);
COMMENT ON COLUMN
    "produtos"."situacao_produto" IS 'Situação do produto
    `A` Ativo 
    `I` Inativo"';
COMMENT ON COLUMN
    "produtos"."peso_liquido" IS 'Peso líquido em KG';
COMMENT ON COLUMN
    "produtos"."peso_bruto" IS 'Peso líquido em KG';
COMMENT ON COLUMN
    "produtos"."volumes" IS 'Quantidade total de volumes que o produto precisa ser dividido para entrega';
COMMENT ON COLUMN
    "produtos"."itens_por_caixa" IS 'Quantidade de itens por caixa/embalagem';
COMMENT ON COLUMN
    "produtos"."gtin" IS 'Código GTIN (GTIN-8, GTIN-12, GTIN-13 ou GTIN-14) do produto que está sendo comercializado';
COMMENT ON COLUMN
    "produtos"."gtin_embalagem" IS 'Código GTIN (GTIN-8, GTIN-12 ou GTIN-13) da menor unidade comercializada no varejo';
COMMENT ON COLUMN
    "produtos"."frete_gratis" IS 'Frete grátis
    Valor default: `false`';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_depositos"(
    "id_bling"              BIGINT PRIMARY KEY  NOT NULL,
    "descricao"             VARCHAR(45)         NOT NULL  CHECK ("descricao" <> ''),
    "situacao"              BOOLEAN             NOT NULL DEFAULT TRUE,
    "padrao"                BOOLEAN             NOT NULL DEFAULT TRUE,
    "desconsiderar_saldo"   BOOLEAN             NOT NULL DEFAULT FALSE
);
COMMENT ON COLUMN
    "produtos_depositos"."situacao" IS '`0` Inativo
    `1` Ativo';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_estoques"(
    "id"            SERIAL PRIMARY KEY  NOT NULL,
    "id_produto"    BIGINT              NOT NULL REFERENCES "produtos"("id_bling"),
    "id_deposito"   BIGINT              NOT NULL REFERENCES "produtos_depositos"("id_bling"),
    "saldo_fisico"  INTEGER             NOT NULL,
    "saldo_virtual" INTEGER             NOT NULL,
    "alterado_em"   TIMESTAMPTZ         DEFAULT current_timestamp
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produto_fornecedor"(
    "id_bling"      BIGINT PRIMARY KEY  NOT NULL,
    "descricao"     VARCHAR(150),
    "codigo"        VARCHAR(20),
    "preco_custo"   INTEGER             NOT NULL,
    "preco_compra"  INTEGER             NOT NULL,
    "padrao"        BOOLEAN             NOT NULL,
    "id_produto"    BIGINT              NOT NULL REFERENCES "produtos"("id_bling"),
    "id_fornecedor" BIGINT              REFERENCES "contatos"("id_bling")
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produto_variacao"(
    "id"                SERIAL PRIMARY KEY  NOT NULL,
    "id_produto_pai"    BIGINT              NOT NULL REFERENCES "produtos"("id_bling"),
    "id_produto_filho"  BIGINT              NOT NULL UNIQUE REFERENCES "produtos"("id_bling"),
    "nome"              VARCHAR(120)        NOT NULL CHECK ("nome" <> ''),
    "ordem"             INTEGER             NOT NULL,
    "clone_pai"         BOOLEAN             NOT NULL
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "produtos_midias_relacao"(
    	"id"            SERIAL PRIMARY KEY  NOT NULL
    ,	"id_produto"    BIGINT              NOT NULL --REFERENCES "produtos"("id_bling")  ON DELETE CASCADE
    ,	"id_image"      INTEGER             NOT NULL REFERENCES "produtos_midias"("id")  ON DELETE CASCADE
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contas_contabeis"(
    "id_bling"  BIGINT PRIMARY KEY  NOT NULL,
    "nome"      VARCHAR(45)         NOT NULL  CHECK ("nome" <> '')
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "categorias_receitas_despesas_tipo"(
    "id"    INTEGER PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(25)         NOT NULL CHECK ("nome" <> '')
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
    "condicao"          VARCHAR(5)          NOT NULL,
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
    "id_transacao"                  VARCHAR(63),
    "link_qr_code_pix"              TEXT,
    "link_boleto"                   TEXT,
    "data_emissao"                  DATE                NOT NULL DEFAULT NOW(),
    "id_contato"                    BIGINT              NOT NULL REFERENCES "contatos"("id_bling"),
    "id_forma_pagamento"            BIGINT              REFERENCES "formas_pagamento"("id_bling"),
    "saldo"                         INTEGER             NOT NULL,
    "vencimento_original"           DATE                NOT NULL DEFAULT NOW(),
    "numero_documento"              VARCHAR(63)         CHECK ("numero_documento" <> ''),
    "competencia"                   DATE                NOT NULL,
    "historico"                     TEXT                NOT NULL,
    "numero_banco"                  VARCHAR(63),
    "id_portador"                   BIGINT              REFERENCES "contas_contabeis"("id_bling"),
    "id_categoria_receita_despesa"  BIGINT              NOT NULL REFERENCES "categorias_receitas_despesas"("id_bling"),
    "id_vendedor"                   BIGINT              REFERENCES "vendedores"("id_bling"),
    "id_tipo_ocorrencia"            INTEGER             REFERENCES "contas_tipo_ocorrencia"("id"),
    "considerar_dias_uteis"         BOOLEAN,
    "dia_vencimento"                DATE                DEFAULT NOW(),
    "numero_parcelas"               INTEGER,
    "data_limite"                   DATE                DEFAULT NOW(),
    "alterado_em"                   TIMESTAMPTZ         DEFAULT current_timestamp
);
COMMENT ON COLUMN
    "contas_receitas_despesas"."saldo" IS 'É calculado subtraindo os valores dos recebimentos do valor da conta';
COMMENT ON COLUMN
    "contas_receitas_despesas"."numero_documento" IS '"Número para controle interno da empresa"';
COMMENT ON COLUMN
    "contas_receitas_despesas"."historico" IS '"Descriçao da conta para controle interno da empresa"';
COMMENT ON COLUMN
    "contas_receitas_despesas"."numero_banco" IS '"Adicionado automaticamente com o número preenchido no cadastro do banco"';
COMMENT ON COLUMN
    "contas_receitas_despesas"."id_tipo_ocorrencia" IS '`1` Única `2` Parcelada `3` Mensal `4` Bimestral `5` Trimestral `6` Semestral `7` Anual `8` Quinzenal `9` Semanal';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contas_origem_situacoes"(
        "id"      SERIAL PRIMARY KEY  NOT NULL
    ,   "nome"    VARCHAR(31)         NOT NULL
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contas_origens"(
        "id"                        SERIAL PRIMARY KEY  NOT NULL
    ,   "id_origem"                 BIGINT              NOT NULL
    ,   "id_conta"                  BIGINT              NOT NULL REFERENCES "contas_receitas_despesas"("id_bling") ON DELETE CASCADE
    ,   "tipo_origem"               VARCHAR(63)
    ,   "numero"                    VARCHAR(63)
    ,   "data_emissao"              DATE
    ,   "valor"                     INTEGER             NOT NULL
    ,   "id_conta_origem_situacao"  INTEGER             NOT NULL REFERENCES "contas_origem_situacoes"("id")
    ,   "url"                       TEXT
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "borderos"(
        "id_bling"                      BIGINT PRIMARY KEY  NOT NULL
    ,   "data"                          DATE                NOT NULL
    ,   "historico"                     TEXT
    ,   "id_portador"                   BIGINT              NOT NULL REFERENCES "contas_contabeis"("id_bling")
    ,   "id_categoria_receita_despesa"  BIGINT              NOT NULL REFERENCES "categorias_receitas_despesas"("id_bling")
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "pagamentos"(
        "id"                SERIAL PRIMARY KEY  NOT NULL
    ,   "id_bordero"        BIGINT              NOT NULL REFERENCES "borderos"("id_bling")  ON DELETE CASCADE
    ,   "id_contato"        BIGINT              NOT NULL REFERENCES "contatos"("id_bling")
    ,   "numero_documento"  VARCHAR(63)
    ,   "valor_pago"        INTEGER             NOT NULL
    ,   "juros"             INTEGER             NOT NULL
    ,   "desconto"          INTEGER             NOT NULL
    ,   "acrescimo"         INTEGER             NOT NULL
    ,   "tarifa"            INTEGER             NOT NULL
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contas_borderos_relacao"(
        "id"            SERIAL PRIMARY KEY  NOT NULL
    ,   "id_conta"      BIGINT              NOT NULL REFERENCES "contas_receitas_despesas"("id_bling")  ON DELETE CASCADE
    ,   "id_bordero"    BIGINT              NOT NULL REFERENCES "borderos"("id_bling")  ON DELETE CASCADE
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "modulos"(
    "id_bling"          BIGINT PRIMARY KEY  NOT NULL,
    "nome"              VARCHAR(45)         NOT NULL CHECK ("nome" <> ''),
    "descricao"         VARCHAR(120)        NOT NULL CHECK ("descricao" <> ''),
    "criar_situacoes"   BOOLEAN             NOT NULL
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "situacoes"(
    "id_bling"  BIGINT PRIMARY KEY  NOT NULL,
    "id_modulo" BIGINT              NOT NULL REFERENCES "modulos"("id_bling"),
    "nome"      VARCHAR(45)         NOT NULL CHECK ("nome" <> ''),
    "cor"       VARCHAR(7)          NOT NULL CHECK ("cor" <> '')
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "transporte_frete_por_conta_de"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(63)         NOT NULL CHECK ("nome" <> '')
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
    "id"      	    SERIAL PRIMARY KEY  NOT NULL,
    "nome"          VARCHAR(63),
    "id_endereco"   INTEGER             NOT NULL REFERENCES "enderecos"("id")
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "vendas"(
    "id_bling"                      BIGINT PRIMARY KEY  NOT NULL,
    "numero"                        INTEGER             NOT NULL,
    "numero_loja"                   VARCHAR(45),
    "data"                          TIMESTAMPTZ         NOT NULL DEFAULT current_timestamp,
    "data_saida"                    DATE                DEFAULT NOW(),
    "data_prevista"                 DATE,
    "id_contato"                    BIGINT              NOT NULL REFERENCES "contatos"("id_bling"),
    "id_situacao"                   BIGINT              NOT NULL REFERENCES "situacoes"("id_bling"),
    "situacao_valor"                INTEGER             NOT NULL,
    "id_loja"                       INTEGER             NOT NULL,
    "numero_pedido_compra"          VARCHAR(45),
    "outras_despesas"               INTEGER             NOT NULL,
    "observacoes"                   TEXT,
    "observacoes_internas"          TEXT,
    "desconto"                      INTEGER             NOT NULL,
    "desconto_unidade"              VARCHAR(12)             NOT NULL,
    "id_categoria"                  BIGINT              REFERENCES "categorias_receitas_despesas"("id_bling"),
    "id_nota_fiscal"                BIGINT,
    "total_icms"                    INTEGER,
    "total_ipi"                     INTEGER,
    "id_vendedor"                   BIGINT              REFERENCES "vendedores"("id_bling"),
    "transporte_id_frete_por_conta" INTEGER             NOT NULL REFERENCES "transporte_frete_por_conta_de"("id"),
    "transporte_valor_frete"        INTEGER             NOT NULL,
    "transporte_quantidade_volumes" INTEGER,
    "transporte_peso_bruto"         INTEGER,
    "transporte_prazo_entrega"      INTEGER,
    "transporte_id_contato"         BIGINT              REFERENCES "contatos"("id_bling"),
    "transporte_id_etiqueta"        INTEGER             REFERENCES "transporte_etiqueta"("id"),
    "alterado_em"                   TIMESTAMPTZ         DEFAULT current_timestamp
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
COMMENT ON COLUMN
    "vendas"."transporte_id_contato" IS 'transportador';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "transporte_volumes"(
    "id_bling"              BIGINT PRIMARY KEY  NOT NULL,
    "id_venda"         	    BIGINT              NOT NULL REFERENCES "vendas"("id_bling"),
    "servico"               VARCHAR(45),
    "codigo_rastreamento"   VARCHAR(45)
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "vendas_itens_produtos"(
    "id_bling"      BIGINT PRIMARY KEY  NOT NULL,
    "id_venda"      BIGINT              NOT NULL REFERENCES "vendas"("id_bling"),
    "id_produto"    BIGINT              REFERENCES "produtos"("id_bling"),
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
    "data_vencimento"       DATE                NOT NULL DEFAULT NOW(),
    "valor"                 INTEGER             NOT NULL,
    "observacoes"           VARCHAR(120)        CHECK ("observacoes" <> ''),
    "id_forma_pagamento"    BIGINT              NOT NULL REFERENCES "formas_pagamento"("id_bling"),
    "id_conta_receber"      BIGINT              REFERENCES "contas_receitas_despesas"("id_bling") ON DELETE CASCADE
);
COMMENT ON COLUMN
    "parcelas"."id_bling" IS 'id contas a receber';

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "atualizacoes_modulos"(
      "id"       SERIAL       PRIMARY KEY NOT NULL
    , "datetime" TIMESTAMPTZ              NOT NULL DEFAULT current_timestamp
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "contagem_estoque"(
        "id"                SERIAL       PRIMARY KEY NOT NULL
    ,   "id_produto"        BIGINT                   NOT NULL UNIQUE REFERENCES "produtos"("id_bling")
    ,   "codigo"            VARCHAR(120)             NOT NULL
    ,   "quantidade_lida"   INTEGER                  NOT NULL
    ,   "datetime"          TIMESTAMPTZ              NOT NULL DEFAULT current_timestamp
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "registros_de_estoque"(
        "id_bling"      SERIAL       PRIMARY KEY NOT NULL
    ,   "id_produto"    BIGINT                   NOT NULL REFERENCES "produtos"("id_bling")
    ,   "id_deposito"   BIGINT                   NOT NULL REFERENCES "produtos_depositos"("id_bling")
    ,   "operacao"      CHAR(1)                  NOT NULL
    ,   "quantidade"    INTEGER                  NOT NULL
    ,   "preco"         INTEGER                  NOT NULL
    ,   "custo"         INTEGER                  NOT NULL
    ,   "observacoes"   VARCHAR(100)             NOT NULL
    ,   "datetime"      TIMESTAMPTZ              NOT NULL DEFAULT current_timestamp
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

CREATE TABLE "registros_de_comparacao_balanco"(
        "id"            SERIAL       PRIMARY KEY NOT NULL
    ,   "id_produto"    BIGINT                   NOT NULL REFERENCES "produtos"("id_bling")
    ,   "id_deposito"   BIGINT                   NOT NULL REFERENCES "produtos_depositos"("id_bling")
    ,   "saldo_antes"   INTEGER                  NOT NULL
    ,   "saldo_depois"  INTEGER                  NOT NULL
    ,   "date"          DATE                     NOT NULL DEFAULT NOW()
);

---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
