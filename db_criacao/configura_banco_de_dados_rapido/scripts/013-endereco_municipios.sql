CREATE TABLE "endereco_municipios"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "nome"  VARCHAR(63),
    "id_uf" INTEGER             NOT NULL REFERENCES "endereco_unidade_federativa"("id")
    
    , CONSTRAINT uq_municipio_iduf UNIQUE ("nome", "id_uf")
);
COMMENT ON TABLE
    "endereco_municipios" IS 'Bloqueio para repetir o mesmo município em um mesmo UF';
