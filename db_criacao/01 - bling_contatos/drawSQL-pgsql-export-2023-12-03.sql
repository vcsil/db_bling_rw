--------------------------------------------------------
--------------------#   CONTATOS   #--------------------

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
    "inscricao_estadual"                VARCHAR(12),
    "rg"                                VARCHAR(10),
    "orgao_emissor"                     VARCHAR(55),
    "email"                             VARCHAR(255),
    "data_nascimento"                   DATE,
    "sexo"                              INTEGER             NOT NULL CHECK (sexo IN (1, 2, 3)) DEFAULT 2,
    "id_classificacao_contato"          BIGINT                       REFERENCES "contatos_classificacao"("id_bling"),
    "cliente_desde"			TIMESTAMPTZ	    NOT NULL DEFAULT current_timestamp
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
