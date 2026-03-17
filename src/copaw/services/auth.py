# -*- coding: utf-8 -*-
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
"""User authentication service."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    jwt = None
    JWT_AVAILABLE = False

from ..config.auth import auth_settings
from ..db.database import db, JWT_AVAILABLE as DB_JWT_AVAILABLE


# Check if JWT is available
if not JWT_AVAILABLE or not DB_JWT_AVAILABLE:
    raise ImportError(
        "JWT is required for authentication. "
        "Please install it with: pip install PyJWT"
    )


class UserService:
    """User management service."""

    @staticmethod
    def _hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash password with salt using PBKDF2-HMAC-SHA256."""
        if salt is None:
            salt = secrets.token_hex(16)
        # Use PBKDF2 with SHA256 for password hashing
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000,  # iterations
        ).hex()
        return password_hash, salt

    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash."""
        computed_hash, _ = UserService._hash_password(password, salt)
        return secrets.compare_digest(computed_hash, password_hash)

    @staticmethod
    def create_token(user_id: int, username: str) -> str:
        """Create JWT token for authenticated user."""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=auth_settings.jwt_expiration_minutes)
        to_encode = {
            "sub": str(user_id),
            "username": username,
            "exp": expire,
            "iat": now,
        }
        return jwt.encode(
            to_encode,
            auth_settings.jwt_secret_key,
            algorithm=auth_settings.jwt_algorithm,
        )

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(
                token,
                auth_settings.jwt_secret_key,
                algorithms=[auth_settings.jwt_algorithm],
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    async def create_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Create a new user."""
        password_hash, salt = self._hash_password(password)
        created_at = datetime.now(timezone.utc)

        async with db.acquire() as conn:
            # Check if user already exists
            existing = await conn.fetchrow(
                "SELECT id FROM users WHERE username = $1",
                username,
            )
            if existing:
                return None

            # Insert new user
            row = await conn.fetchrow(
                """
                INSERT INTO users (username, password_hash, salt, created_at)
                VALUES ($1, $2, $3, $4)
                RETURNING id, username, created_at
                """,
                username,
                password_hash,
                salt,
                created_at,
            )
            return dict(row) if row else None

    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password."""
        async with db.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, username, password_hash, salt FROM users WHERE username = $1",
                username,
            )
            if not row:
                return None

            user_data = dict(row)
            if not self.verify_password(
                password,
                user_data["password_hash"],
                user_data["salt"],
            ):
                return None

            # Return user data without sensitive fields
            return {
                "id": user_data["id"],
                "username": user_data["username"],
            }

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        async with db.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, username, created_at FROM users WHERE id = $1",
                user_id,
            )
            return dict(row) if row else None


# Global service instance
user_service = UserService()
