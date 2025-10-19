#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Application settings module."""
from __future__ import annotations

from functools import lru_cache
from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load the environment variables from the .env file as early as possible.
load_dotenv()


class Settings(BaseSettings):
    """Centralised application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    bling_client_id: Annotated[str, Field(alias="BLING_CLIENT_ID", min_length=1)]
    bling_client_secret: Annotated[str, Field(alias="BLING_CLIENT_SECRET", min_length=1)]
    bling_usuario: Annotated[str, Field(alias="BLING_USUARIO", min_length=1)]
    bling_senha_usuario: Annotated[str, Field(alias="BLING_SENHA_USUARIO", min_length=1)]

    postgres_user: Annotated[str, Field(alias="POSTGRES_USER", min_length=1)]
    postgres_password: Annotated[str, Field(alias="POSTGRES_PASSWORD", min_length=1)]
    postgres_host: Annotated[
        str,
        Field(alias="POSTGRES_HOST", min_length=1, pattern=r"^[A-Za-z0-9_.-]+$"),
    ]
    postgres_container_port: Annotated[
        int,
        Field(alias="POSTGRES_CONTAINER_PORT", ge=1, le=65535),
    ]
    postgres_host_port: Annotated[
        int,
        Field(alias="POSTGRES_HOST_PORT", ge=1, le=65535),
    ]
    postgres_db: Annotated[str, Field(alias="POSTGRES_DB", min_length=1)]
    postgres_tz: Annotated[
        str,
        Field(alias="POSTGRES_TZ", default="America/Sao_Paulo", min_length=1),
    ]

    oauth_baseurl: Annotated[AnyHttpUrl, Field(alias="OAUTH_BASEURL")]

    @field_validator(
        "bling_client_id",
        "bling_client_secret",
        "bling_usuario",
        "bling_senha_usuario",
        "postgres_user",
        "postgres_password",
        "postgres_db",
        mode="after",
    )
    @classmethod
    def _no_blank_values(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Value cannot be blank or whitespace only")
        return value

    @field_validator("postgres_tz", mode="after")
    @classmethod
    def _validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown timezone: {value}") from exc
        return value


@lru_cache()
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()
