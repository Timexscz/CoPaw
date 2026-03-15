# -*- coding: utf-8 -*-
"""Authentication API routes."""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request, Body
from pydantic import BaseModel, Field

from ...services.auth import user_service
from ...config import load_config
from ...config.auth import auth_settings

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Login request body."""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    """Registration request body."""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class AuthResponse(BaseModel):
    """Authentication response."""
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str


def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user from token if present (optional)."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1]
    payload = user_service.verify_token(token)
    if not payload:
        return None

    return {
        "id": int(payload["sub"]),
        "username": payload["username"],
    }


async def get_current_user(request: Request) -> Dict[str, Any]:
    """Get current user from token (required)."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ", 1)[1]
    payload = user_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": int(payload["sub"]),
        "username": payload["username"],
    }


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest) -> AuthResponse:
    """Login with username and password."""
    # Check if auth is enabled
    config = load_config()
    if not config.auth.enabled:
        # If auth is not enabled, return a dummy token
        return AuthResponse(
            access_token="auth_disabled",
            user={"id": 0, "username": "anonymous"},
        )

    user = await user_service.authenticate_user(
        request.username,
        request.password,
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        )

    token = user_service.create_token(user["id"], user["username"])
    return AuthResponse(
        access_token=token,
        user=user,
    )


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest) -> AuthResponse:
    """Register a new user."""
    # Check if auth is enabled
    config = load_config()
    if not config.auth.enabled:
        raise HTTPException(
            status_code=403,
            detail="Registration is disabled",
        )

    if not config.auth.allow_registration:
        raise HTTPException(
            status_code=403,
            detail="New user registration is not allowed",
        )

    # Check if username already exists
    user = await user_service.create_user(
        request.username,
        request.password,
    )
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists",
        )

    token = user_service.create_token(user["id"], user["username"])
    return AuthResponse(
        access_token=token,
        user=user,
    )


@router.get("/me", response_model=Dict[str, Any])
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current user info."""
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> MessageResponse:
    """Logout (client should discard token)."""
    # JWT is stateless, so we just inform the client to discard the token
    return MessageResponse(message="Logged out successfully")


@router.get("/status")
async def auth_status(request: Request) -> Dict[str, Any]:
    """Get authentication status and configuration."""
    config = load_config()
    current_user = get_current_user_optional(request)

    return {
        "enabled": config.auth.enabled,
        "allow_registration": config.auth.allow_registration,
        "authenticated": current_user is not None,
        "user": current_user,
    }
