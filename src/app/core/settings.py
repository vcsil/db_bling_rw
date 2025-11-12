#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Application settings module."""
from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Mapping, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import find_dotenv, load_dotenv, set_key
from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH: str = find_dotenv(usecwd=True) or ".env"


class Settings(BaseSettings):
    """Centralised application configuration."""

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    timezone_app: Annotated[
        str,
        Field(alias="TIMEZONE_APP", default="UTC", min_length=1),
    ]
    timezone_business: Annotated[
        str,
        Field(alias="TIMEZONE_BUSINESS", default="America/Sao_Paulo", min_length=1),
    ]

    bling_client_id: Annotated[str, Field(alias="BLING_CLIENT_ID", min_length=1)]
    bling_client_secret: Annotated[str, Field(alias="BLING_CLIENT_SECRET", min_length=1)]
    bling_usuario: Annotated[str, Field(alias="BLING_USUARIO", min_length=1)]
    bling_senha_usuario: Annotated[str, Field(alias="BLING_SENHA_USUARIO", min_length=1)]
    bling_baseurl: Annotated[AnyHttpUrl, Field(alias="BLING_BASEURL")]

    bling_oauth_access_token: Annotated[
        Optional[str],
        Field(alias="BLING_OAUTH_ACCESS_TOKEN", default=None, min_length=1),
    ]
    bling_oauth_expires_in: Annotated[
        Optional[str],
        Field(alias="BLING_OAUTH_EXPIRES_IN", default=None, min_length=1),
    ]
    bling_oauth_refresh_token: Annotated[
        Optional[str],
        Field(alias="BLING_OAUTH_REFRESH_TOKEN", default=None, min_length=1),
    ]
    bling_oauth_scope: Annotated[
        Optional[str],
        Field(alias="BLING_OAUTH_SCOPE", default=None),
    ]

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

    @field_validator(
        "bling_client_id",
        "bling_client_secret",
        "bling_usuario",
        "bling_senha_usuario",
        "postgres_user",
        "postgres_password",
        "postgres_host",
        "postgres_db",
        mode="after",
    )
    @classmethod
    def _no_blank_values(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Value cannot be blank or whitespace only")
        return value

    @field_validator(
        "timezone_app",
        "timezone_business",
        "postgres_tz",
        mode="after"
    )
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


def set_settings(
    updates: Mapping[str, Optional[str]] | None = None,
    /,
    *,
    env_path: Optional[str] = None,
    **extra_updates: Optional[str],
) -> Settings:
    """Update configuration values and persist them to the ``.env`` file.

    The provided ``updates`` mapping and additional keyword arguments are merged,
    written to the resolved ``.env`` path and the cached settings instance is
    refreshed to reflect the new values.
    """
    load_dotenv(dotenv_path=ENV_PATH)

    merged_updates: dict[str, Optional[str]] = {}
    if updates:
        merged_updates.update(updates)
    if extra_updates:
        merged_updates.update(extra_updates)
    if not merged_updates:
        return get_settings()

    resolved_env_path = env_path or ENV_PATH

    try:
        for key, value in merged_updates.items():
            set_key(resolved_env_path, key, "" if value is None else str(value), quote_mode="never")
    except OSError as exc:
        raise OSError(f"Falha ao persistir configurações em {resolved_env_path}") from exc

    load_dotenv(dotenv_path=resolved_env_path, override=True)
    get_settings.cache_clear()
    return get_settings()
