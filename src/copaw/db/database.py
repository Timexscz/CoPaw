# -*- coding: utf-8 -*-
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
"""Database connection management for PostgreSQL and Redis."""

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import asyncpg
import redis.asyncio as aioredis
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    jwt = None
    JWT_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()


class DatabaseSettings(BaseSettings):
    """Database connection settings."""

    model_config = SettingsConfigDict(env_prefix="DATABASE_")

    host: str = "localhost"
    port: int = 5432
    user: str = "copaw"
    password: str = "copaw_password"
    name: str = "copaw"

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseSettings):
    """Redis connection settings."""

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None


class Database:
    """Database manager for PostgreSQL and Redis."""
    
    _instance: Optional['Database'] = None
    _pg_pool: Optional[asyncpg.Pool] = None
    _redis: Optional[aioredis.Redis] = None
    
    def __new__(cls) -> 'Database':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self) -> None:
        """Initialize database connections."""
        if self._pg_pool is None:
            self._pg_pool = await asyncpg.create_pool(
                host=settings.host,
                port=settings.port,
                user=settings.user,
                password=settings.password,
                database=settings.name,
                min_size=2,
                max_size=10,
                command_timeout=60,
            )
            await self._init_tables()

        if self._redis is None:
            self._redis = aioredis.from_url(
                f"redis://{redis_settings.host}:{redis_settings.port}",
                encoding="utf-8",
                decode_responses=True,
            )
    
    async def disconnect(self) -> None:
        """Close database connections."""
        if self._pg_pool:
            await self._pg_pool.close()
            self._pg_pool = None

        if self._redis:
            await self._redis.aclose()
            self._redis = None
    
    async def _init_tables(self) -> None:
        """Initialize database tables from migration files if not exist."""
        migrations_dir = Path(__file__).parent / "migrations"
        if not migrations_dir.exists():
            return

        # Get list of migration files in order
        migration_files = sorted(migrations_dir.glob("*.sql"))

        async with self._pg_pool.acquire() as conn:
            # Check which tables already exist
            existing_tables = await conn.fetch("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema='public'
            """)
            existing_table_names = {row["table_name"] for row in existing_tables}

            # Run migrations in order
            for sql_file in migration_files:
                # Skip if it's the categories migration and categories table exists
                if "001_categories.sql" in str(sql_file) and "categories" in existing_table_names:
                    continue

                # For users migration, check if users table exists
                if "002_users.sql" in str(sql_file) and "users" in existing_table_names:
                    continue

                sql = sql_file.read_text()
                await conn.execute(sql)
    
    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Acquire a PostgreSQL connection from the pool."""
        if self._pg_pool is None:
            await self.connect()
        async with self._pg_pool.acquire() as conn:
            yield conn
    
    @property
    def redis(self) -> aioredis.Redis:
        """Get Redis client."""
        if self._redis is None:
            asyncio.create_task(self.connect())
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._redis


# Global settings and database instances
settings = DatabaseSettings()
redis_settings = RedisSettings()
db = Database()


@asynccontextmanager
async def get_db() -> AsyncGenerator[Database, None]:
    """Dependency injection for database connection."""
    await db.connect()
    try:
        yield db
    finally:
        # Keep connection alive
        pass
