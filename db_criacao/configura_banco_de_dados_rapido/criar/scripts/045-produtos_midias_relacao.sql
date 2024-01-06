CREATE TABLE "produtos_midias_relacao"(
    "id"            SERIAL PRIMARY KEY  NOT NULL,
    "id_produto"    BIGINT              NOT NULL REFERENCES "produtos"("id_bling"),
    "id_image"      INTEGER             NOT NULL REFERENCES "produtos_midias"("id")
);