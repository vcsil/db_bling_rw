CREATE TABLE "transporte_etiqueta"(
    "id"      	    SERIAL PRIMARY KEY  NOT NULL,
    "nome"          VARCHAR(63),
    "id_endereco"   INTEGER             NOT NULL REFERENCES "enderecos"("id")
);
