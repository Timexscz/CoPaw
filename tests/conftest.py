#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test configuration for pytest.
Loads environment variables from .env file for testing.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment from {env_path}")
else:
    print("⚠ No .env file found, using default values")

# Set test-specific environment variables
os.environ.setdefault("DATABASE_HOST", "192.168.1.3")
os.environ.setdefault("DATABASE_PORT", "4434")
os.environ.setdefault("DATABASE_USER", "copaw")
os.environ.setdefault("DATABASE_PASSWORD", "BRiwTeysYcc7x2AN")
os.environ.setdefault("DATABASE_NAME", "copaw")

# Redis configuration
os.environ.setdefault("REDIS_HOST", "192.168.1.3")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_PASSWORD", "redis_3DfA4K")

# Auth configuration for testing
os.environ.setdefault("AUTH_ENABLED", "true")
os.environ.setdefault("AUTH_ALLOW_REGISTRATION", "true")
if not os.environ.get("AUTH_JWT_SECRET_KEY"):
    # Generate a secure random key for testing
    import secrets
    os.environ["AUTH_JWT_SECRET_KEY"] = secrets.token_urlsafe(32)

print("✓ Test environment configured")
print(f"  Database: {os.environ.get('DATABASE_HOST')}:{os.environ.get('DATABASE_PORT')}/{os.environ.get('DATABASE_NAME')}")
print(f"  Redis: {os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}")
print(f"  Auth Enabled: {os.environ.get('AUTH_ENABLED')}")
