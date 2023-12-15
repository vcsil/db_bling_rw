CREATE TABLE "endereco_bairros"(
    "id"            SERIAL PRIMARY KEY  NOT NULL,
    "nome"          VARCHAR(63),
    "id_municipio"  INTEGER             NOT NULL REFERENCES "endereco_municipios"("id")
    
    , CONSTRAINT uq_bairro_idmunicipio UNIQUE ("nome", "id_municipio")
);
COMMENT ON TABLE
    "endereco_bairros" IS 'Bloqueio para repetir o mesmo bairro em um mesmo município';
