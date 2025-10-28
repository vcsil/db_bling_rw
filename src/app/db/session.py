#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 19 15:41:12 2025

Database session and engine helpers.

@author: vcsil
"""

from __future__ import annotations

from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.app.core.settings import Settings, get_settings


_LOCALHOST_IDENTIFIERS = {"localhost", "127.0.0.1"}


def _choose_port(settings: Settings) -> int:
    """Return the most appropriate port for the configured PostgreSQL host."""

    if settings.postgres_host in _LOCALHOST_IDENTIFIERS:
        return settings.postgres_host_port
    return settings.postgres_container_port


def get_async_database_url(settings: Settings) -> str:
    """Build the async database URL based on the project settings."""

    return str(
        URL.create(
            "postgresql+psycopg_async",
            username=settings.postgres_user,
            password=settings.postgres_password,
            host=settings.postgres_host,
            port=_choose_port(settings),
            database=settings.postgres_db,
        )
    )


def get_sync_database_url(settings: Settings) -> str:
    """Build the sync database URL for tools like Alembic."""

    return str(
        URL.create(
            "postgresql+psycopg",
            username=settings.postgres_user,
            password=settings.postgres_password,
            host=settings.postgres_host,
            port=_choose_port(settings),
            database=settings.postgres_db,
        )
    )


@lru_cache()
def get_engine() -> AsyncEngine:
    """Return a cached async engine instance configured from the settings."""

    settings = get_settings()
    return create_async_engine(
        get_async_database_url(settings),
        echo=False,
        pool_pre_ping=True,
    )


@lru_cache()
def _get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Return a cached async session factory bound to the engine."""

    return async_sessionmaker(
        bind=get_engine(),
        expire_on_commit=False,
        class_=AsyncSession,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async SQLAlchemy session for FastAPI dependencies or Celery."""

    session_factory = _get_sessionmaker()
    async with session_factory() as session:
        yield session
