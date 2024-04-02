CREATE TABLE "atualizacoes_modulos"(
      "id"       SERIAL       PRIMARY KEY NOT NULL
    , "datetime" TIMESTAMPTZ              NOT NULL DEFAULT current_timestamp
);
