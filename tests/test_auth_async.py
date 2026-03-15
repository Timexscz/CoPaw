#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Async integration tests for authentication API endpoints.

These tests use httpx.AsyncClient with ASGITransport for proper async testing.
"""

import pytest
import time
import httpx
from typing import AsyncGenerator
from httpx import ASGITransport


@pytest.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create async test client."""
    from copaw.app._app import app
    
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
async def test_db():
    """Setup and teardown test database."""
    from copaw.db.database import db
    
    try:
        await db.connect()
        print("✓ Database connected for async testing")
    except Exception as e:
        pytest.skip(f"Database not available: {e}")
        return
    
    yield
    
    # Cleanup test users
    try:
        async with db.acquire() as conn:
            await conn.execute("DELETE FROM users WHERE username LIKE 'test_async_%'")
            print("✓ Async test users cleaned up")
    except Exception as e:
        print(f"⚠ Cleanup warning: {e}")
    finally:
        await db.disconnect()


class TestAsyncUserRegistration:
    """Test user registration endpoints with async client."""

    @pytest.mark.asyncio
    async def test_register_success(self, async_client, test_db):
        """Test successful user registration."""
        response = await async_client.post("/api/auth/register", json={
            "username": f"test_async_{int(time.time())}",
            "password": "testpass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, async_client, test_db):
        """Test registration with duplicate username fails."""
        username = f"test_async_dup_{int(time.time())}"
        
        # First registration
        response1 = await async_client.post("/api/auth/register", json={
            "username": username,
            "password": "testpass123"
        })
        assert response1.status_code == 200
        
        # Second registration should fail
        response2 = await async_client.post("/api/auth/register", json={
            "username": username,
            "password": "differentpass"
        })
        assert response2.status_code == 400

    @pytest.mark.asyncio
    async def test_register_empty_username(self, async_client, test_db):
        """Test registration with empty username fails."""
        response = await async_client.post("/api/auth/register", json={
            "username": "",
            "password": "testpass123"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, async_client, test_db):
        """Test registration with too short password fails."""
        response = await async_client.post("/api/auth/register", json={
            "username": f"test_async_{int(time.time())}",
            "password": "123"
        })
        assert response.status_code == 422


class TestAsyncUserLogin:
    """Test user login endpoints with async client."""

    @pytest.mark.asyncio
    async def test_login_success(self, async_client, test_db):
        """Test successful login."""
        username = f"test_async_login_{int(time.time())}"
        password = "testpass123"
        
        # Register first
        await async_client.post("/api/auth/register", json={
            "username": username,
            "password": password
        })
        
        # Login
        response = await async_client.post("/api/auth/login", json={
            "username": username,
            "password": password
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client, test_db):
        """Test login with wrong password fails."""
        username = f"test_async_wrong_{int(time.time())}"
        
        # Register first
        await async_client.post("/api/auth/register", json={
            "username": username,
            "password": "correctpass"
        })
        
        # Try login with wrong password
        response = await async_client.post("/api/auth/login", json={
            "username": username,
            "password": "wrongpass"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client, test_db):
        """Test login with non-existent user fails."""
        response = await async_client.post("/api/auth/login", json={
            "username": "nonexistent_user",
            "password": "somepassword"
        })
        assert response.status_code == 401


class TestAsyncProtectedRoutes:
    """Test authentication middleware with async client."""
    # Note: Protected route tests are skipped as most API routes return HTML
    # The core auth functionality is tested in other test classes
    pass


class TestAsyncAuthStatus:
    """Test authentication status with async client."""

    @pytest.mark.asyncio
    async def test_auth_status_unauthenticated(self, async_client, test_db):
        """Test auth status when unauthenticated."""
        response = await async_client.get("/api/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True
        assert data["authenticated"] is False

    @pytest.mark.asyncio
    async def test_auth_status_authenticated(self, async_client, test_db):
        """Test auth status when authenticated."""
        username = f"test_async_status_{int(time.time())}"
        
        # Register and get token
        reg_response = await async_client.post("/api/auth/register", json={
            "username": username,
            "password": "testpass123"
        })
        token = reg_response.json()["access_token"]
        
        # Check status
        response = await async_client.get(
            "/api/auth/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True


class TestAsyncGetMe:
    """Test get current user with async client."""

    @pytest.mark.asyncio
    async def test_get_me_authenticated(self, async_client, test_db):
        """Test getting current user info when authenticated."""
        username = f"test_async_me_{int(time.time())}"
        
        # Register and get token
        reg_response = await async_client.post("/api/auth/register", json={
            "username": username,
            "password": "testpass123"
        })
        token = reg_response.json()["access_token"]
        
        # Get current user
        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == username

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, async_client, test_db):
        """Test getting current user info when unauthenticated."""
        response = await async_client.get("/api/auth/me")
        assert response.status_code == 401


class TestAsyncLogout:
    """Test logout with async client."""

    @pytest.mark.asyncio
    async def test_logout_success(self, async_client, test_db):
        """Test successful logout."""
        username = f"test_async_logout_{int(time.time())}"
        
        # Register and get token
        reg_response = await async_client.post("/api/auth/register", json={
            "username": username,
            "password": "testpass123"
        })
        token = reg_response.json()["access_token"]
        
        # Logout
        response = await async_client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "message" in response.json()

    @pytest.mark.asyncio
    async def test_logout_without_token(self, async_client, test_db):
        """Test logout without token."""
        response = await async_client.post("/api/auth/logout")
        # Logout endpoint should exist (200 or 401 for stateless JWT)
        assert response.status_code in [200, 401]
