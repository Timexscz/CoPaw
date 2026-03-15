# -*- coding: utf-8 -*-
"""Authentication configuration and settings."""

import os
import secrets
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """Authentication settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="AUTH_")

    # JWT Settings
    jwt_secret_key: str = Field(
        default_factory=lambda: os.getenv("AUTH_JWT_SECRET_KEY") or secrets.token_urlsafe(32),
        description="Secret key for JWT token encoding/decoding",
    )
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = Field(
        default=1440,  # 24 hours
        description="JWT token expiration time in minutes",
    )

    # Security Settings
    enabled: bool = Field(
        default=False,
        description="Whether authentication is enabled",
    )
    allow_registration: bool = Field(
        default=True,
        description="Whether new user registration is allowed",
    )

    # Session Settings
    session_max_age_days: int = 30


class OAuthConfig(BaseModel):
    """OAuth configuration for external providers (optional)."""

    model_config = {"extra": "allow"}

    # GitHub OAuth
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = ""

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""

    # Generic OAuth2
    enabled: bool = False
    provider: str = ""
    authorization_url: str = ""
    token_url: str = ""
    userinfo_url: str = ""
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = ""
    scope: str = ""


# Global auth settings instance
auth_settings = AuthSettings()
