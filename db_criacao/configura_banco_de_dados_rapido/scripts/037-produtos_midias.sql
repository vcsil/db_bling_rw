CREATE TABLE "produtos_midias"(
    "id"    SERIAL PRIMARY KEY  NOT NULL,
    "tipo"  BOOLEAN             NOT NULL,
    "url"   TEXT                NOT NULL CHECK ("url" <> '')
);
COMMENT ON COLUMN
    "produtos_midias"."tipo" IS 'True: Foto
    False: Video';