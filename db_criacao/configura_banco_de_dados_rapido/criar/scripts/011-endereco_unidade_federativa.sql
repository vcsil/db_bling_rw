CREATE TABLE "endereco_unidade_federativa"(
    "id"        SERIAL PRIMARY KEY  NOT NULL,
    "nome"      VARCHAR(63),	    --NOT NULL CHECK ("nome" <> ''),
    "id_pais"   INTEGER             NOT NULL REFERENCES "endereco_paises"("id")
    
    , CONSTRAINT uq_uf_idpais UNIQUE ("nome", "id_pais")
);
COMMENT ON TABLE
    "endereco_unidade_federativa" IS 'Bloqueio para repetir a mesma UF em um mesmo País';
