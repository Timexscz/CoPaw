#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick test to verify auth API works with .env database.
"""

from fastapi.testclient import TestClient
from copaw.app._app import app

client = TestClient(app, raise_server_exceptions=True)

print("=" * 60)
print("Testing Authentication API with .env database")
print("=" * 60)

# Test 1: Register
print("\n1. Testing user registration...")
response = client.post("/api/auth/register", json={
    "username": f"quick_test_{int(__import__('time').time())}",
    "password": "testpass123"
})
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json() if response.status_code == 200 else response.text[:200]}")

# Test 2: Login
print("\n2. Testing user login...")
response = client.post("/api/auth/login", json={
    "username": "admin",  # Try default user
    "password": "admin123"
})
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print(f"   Token: {response.json()['access_token'][:50]}...")
else:
    print(f"   Response: {response.text[:200]}")

# Test 3: Auth Status
print("\n3. Testing auth status...")
response = client.get("/api/auth/status")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

print("\n" + "=" * 60)
print("API Test Complete")
print("=" * 60)
