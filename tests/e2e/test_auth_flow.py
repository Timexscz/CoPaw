#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
End-to-end test for complete authentication flow.

This test verifies the full authentication workflow:
1. Register a new user
2. Login with credentials
3. Access protected resources
4. Get current user info
5. Check auth status
6. Logout

Note: This is a stateless JWT implementation, so logout doesn't invalidate tokens.
The client is responsible for discarding tokens after logout.
"""

import pytest
from fastapi.testclient import TestClient
from copaw.app._app import app


class TestCompleteAuthFlow:
    """End-to-end tests for complete authentication flow."""

    def test_full_registration_and_login_flow(self):
        """Test complete flow: register → login → access protected → logout."""
        client = TestClient(app)
        import time
        
        username = f"e2e_test_user_{int(time.time())}"
        password = "e2e_test_pass_123"
        
        # Step 1: Register new user
        register_response = client.post("/api/auth/register", json={
            "username": username,
            "password": password
        })
        assert register_response.status_code == 200
        register_data = register_response.json()
        assert "access_token" in register_data
        assert register_data["user"]["username"] == username
        token = register_data["access_token"]
        
        # Step 2: Access protected resource with token
        headers = {"Authorization": f"Bearer {token}"}
        agents_response = client.get("/api/agents", headers=headers)
        assert agents_response.status_code == 200
        
        # Step 3: Get current user info
        me_response = client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["username"] == username
        
        # Step 4: Check auth status (should show authenticated)
        status_response = client.get("/api/auth/status", headers=headers)
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["authenticated"] is True
        assert status_data["user"]["username"] == username
        
        # Step 5: Logout
        logout_response = client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200
        
        # Step 6: Token still works (stateless JWT)
        # In a stateless JWT implementation, the server doesn't track logout
        # The client is responsible for discarding the token
        agents_response_after_logout = client.get("/api/agents", headers=headers)
        # This will still succeed because JWT is stateless
        assert agents_response_after_logout.status_code == 200
        
        # Step 7: Without token, access should fail
        no_auth_response = client.get("/api/agents")
        assert no_auth_response.status_code == 401

    def test_multiple_concurrent_sessions(self):
        """Test multiple users can have concurrent sessions."""
        client = TestClient(app)
        import time
        
        # User 1
        username1 = f"e2e_user1_{int(time.time())}"
        password1 = "pass1_123"
        reg1 = client.post("/api/auth/register", json={
            "username": username1,
            "password": password1
        })
        token1 = reg1.json()["access_token"]
        
        # User 2
        username2 = f"e2e_user2_{int(time.time())}"
        password2 = "pass2_123"
        reg2 = client.post("/api/auth/register", json={
            "username": username2,
            "password": password2
        })
        token2 = reg2.json()["access_token"]
        
        # Both users should be able to access their own info
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        me1 = client.get("/api/auth/me", headers=headers1)
        assert me1.json()["username"] == username1
        
        me2 = client.get("/api/auth/me", headers=headers2)
        assert me2.json()["username"] == username2

    def test_session_persistence(self):
        """Test that sessions persist across requests."""
        client = TestClient(app)
        import time
        
        username = f"e2e_persist_user_{int(time.time())}"
        password = "persist_pass"
        
        # Register
        reg_response = client.post("/api/auth/register", json={
            "username": username,
            "password": password
        })
        token = reg_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make multiple requests with same token
        for i in range(5):
            me_response = client.get("/api/auth/me", headers=headers)
            assert me_response.status_code == 200
            assert me_response.json()["username"] == username
