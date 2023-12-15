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
