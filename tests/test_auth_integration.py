#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integration tests for authentication API endpoints.

These tests verify the complete authentication flow including:
- User registration
- User login
- Token validation
- Protected route access
- Authentication middleware

Note: These tests require a running PostgreSQL database.
Database configuration is loaded from .env file.
"""

import pytest
import time
import asyncio
from fastapi.testclient import TestClient
from copaw.app._app import app
from copaw.db.database import db


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
async def test_db():
    """Setup and teardown test database."""
    # Connect to database
    try:
        await db.connect()
        print("✓ Database connected for testing")
    except Exception as e:
        pytest.skip(f"Database not available: {e}")
        return
    
    yield
    
    # Cleanup test users
    try:
        async with db.acquire() as conn:
            # Delete all test users
            await conn.execute("DELETE FROM users WHERE username LIKE 'test_%'")
            print("✓ Test users cleaned up")
    except Exception as e:
        print(f"⚠ Cleanup warning: {e}")
    finally:
        await db.disconnect()


class TestUserRegistration:
    """Test user registration endpoints."""

    def test_register_success(self, client, test_db):
        """Test successful user registration."""
        response = client.post("/api/auth/register", json={
            "username": f"test_user_{int(time.time())}",
            "password": "testpass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert "id" in data["user"]
        assert "username" in data["user"]

    def test_register_duplicate_username(self, client, test_db):
        """Test registration with duplicate username fails."""
        username = f"test_duplicate_{int(time.time())}"
        password = "testpass123"
        
        # First registration should succeed
        response1 = client.post("/api/auth/register", json={
            "username": username,
            "password": password
        })
        assert response1.status_code == 200
        
        # Second registration with same username should fail
        response2 = client.post("/api/auth/register", json={
            "username": username,
            "password": "differentpass"
        })
        assert response2.status_code == 400

    def test_register_empty_username(self, client, test_db):
        """Test registration with empty username fails."""
        response = client.post("/api/auth/register", json={
            "username": "",
            "password": "testpass123"
        })
        assert response.status_code == 422  # Validation error

    def test_register_empty_password(self, client, test_db):
        """Test registration with empty password fails."""
        response = client.post("/api/auth/register", json={
            "username": f"test_user_{int(time.time())}",
            "password": ""
        })
        assert response.status_code == 422  # Validation error

    def test_register_short_password(self, client, test_db):
        """Test registration with too short password fails."""
        response = client.post("/api/auth/register", json={
            "username": f"test_user_{int(time.time())}",
            "password": "123"  # Too short
        })
        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Test user login endpoints."""

    def test_login_success(self, client, test_db):
        """Test successful login."""
        username = f"test_login_{int(time.time())}"
        password = "testpass123"
        
        # Register first
        client.post("/api/auth/register", json={
            "username": username,
            "password": password
        })
        
        # Login
        response = client.post("/api/auth/login", json={
            "username": username,
            "password": password
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == username

    def test_login_wrong_password(self, client, test_db):
        """Test login with wrong password fails."""
        username = f"test_wrong_pass_{int(time.time())}"
        correct_password = "correctpass"
        wrong_password = "wrongpass"
        
        # Register first
        client.post("/api/auth/register", json={
            "username": username,
            "password": correct_password
        })
        
        # Try login with wrong password
        response = client.post("/api/auth/login", json={
            "username": username,
            "password": wrong_password
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client, test_db):
        """Test login with non-existent user fails."""
        response = client.post("/api/auth/login", json={
            "username": "nonexistent_user",
            "password": "somepassword"
        })
        assert response.status_code == 401

    def test_login_empty_credentials(self, client, test_db):
        """Test login with empty credentials fails."""
        response = client.post("/api/auth/login", json={
            "username": "",
            "password": ""
        })
        assert response.status_code == 422  # Validation error


class TestProtectedRoutes:
    """Test authentication middleware for protected routes."""

    def test_protected_route_without_auth(self, client, test_db):
        """Test accessing protected route without authentication."""
        # When auth is enabled, this should return 401
        # When auth is disabled, this should return 200
        response = client.get("/api/agents")
        # Auth is enabled in .env, so expect 401
        assert response.status_code == 401

    def test_protected_route_with_invalid_token(self, client, test_db):
        """Test accessing protected route with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/agents", headers=headers)
        assert response.status_code == 401

    def test_protected_route_with_valid_token(self, client, test_db):
        """Test accessing protected route with valid token."""
        username = f"test_protected_{int(time.time())}"
        password = "testpass123"
        
        # Register and get token
        reg_response = client.post("/api/auth/register", json={
            "username": username,
            "password": password
        })
        assert reg_response.status_code == 200, f"Registration failed: {reg_response.text}"
        token = reg_response.json()["access_token"]
        
        # Access protected route
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/agents", headers=headers)
        assert response.status_code == 200, f"Protected route access failed: {response.text}"

    def test_public_route_without_auth(self, client, test_db):
        """Test accessing public route without authentication."""
        # These routes should be accessible without auth
        response = client.get("/api/auth/status")
        assert response.status_code == 200
        
        response = client.get("/api/version")
        assert response.status_code == 200


class TestAuthStatus:
    """Test authentication status endpoint."""

    def test_auth_status_unauthenticated(self, client, test_db):
        """Test auth status when unauthenticated."""
        response = client.get("/api/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "authenticated" in data
        # When auth is enabled but no token, should show unauthenticated
        assert data["authenticated"] is False
        assert data["user"] is None

    def test_auth_status_authenticated(self, client, test_db):
        """Test auth status when authenticated."""
        username = f"test_status_{int(time.time())}"
        password = "testpass123"
        
        # Register and get token
        reg_response = client.post("/api/auth/register", json={
            "username": username,
            "password": password
        })
        assert reg_response.status_code == 200, f"Registration failed: {reg_response.text}"
        token = reg_response.json()["access_token"]
        
        # Check status
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/status", headers=headers)
        assert response.status_code == 200, f"Status check failed: {response.text}"
        data = response.json()
        assert data["authenticated"] is True
        assert data["user"] is not None
        assert data["user"]["username"] == username


class TestGetMe:
    """Test get current user endpoint."""

    def test_get_me_authenticated(self, client, test_db):
        """Test getting current user info when authenticated."""
        username = f"test_me_{int(time.time())}"
        password = "testpass123"
        
        # Register and get token
        reg_response = client.post("/api/auth/register", json={
            "username": username,
            "password": password
        })
        assert reg_response.status_code == 200, f"Registration failed: {reg_response.text}"
        token = reg_response.json()["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200, f"Get me failed: {response.text}"
        data = response.json()
        assert data["username"] == username

    def test_get_me_unauthenticated(self, client, test_db):
        """Test getting current user info when unauthenticated."""
        response = client.get("/api/auth/me")
        # When auth is enabled, should return 401
        assert response.status_code == 401


class TestLogout:
    """Test logout endpoint."""

    def test_logout_success(self, client, test_db):
        """Test successful logout."""
        username = f"test_logout_{int(time.time())}"
        password = "testpass123"
        
        # Register and get token
        reg_response = client.post("/api/auth/register", json={
            "username": username,
            "password": password
        })
        assert reg_response.status_code == 200, f"Registration failed: {reg_response.text}"
        token = reg_response.json()["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/auth/logout", headers=headers)
        assert response.status_code == 200, f"Logout failed: {response.text}"
        assert "message" in response.json()

    def test_logout_without_token(self, client, test_db):
        """Test logout without token (should still succeed for stateless JWT)."""
        response = client.post("/api/auth/logout")
        # Logout endpoint should exist and return success
        assert response.status_code == 200


class TestAuthConfig:
    """Test authentication configuration."""

    def test_auth_config_defaults(self, client, test_db):
        """Test default authentication configuration."""
        response = client.get("/api/auth/status")
        assert response.status_code == 200
        data = response.json()
        # By default, auth should be disabled for backward compatibility
        assert "enabled" in data
        assert "allow_registration" in data
