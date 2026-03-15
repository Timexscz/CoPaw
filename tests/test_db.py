#!/usr/bin/env python3
"""Test database connection."""

import asyncio
from copaw.db.database import db, settings

async def test():
    try:
        print(f"Connecting to {settings.host}:{settings.port}/{settings.name}...")
        await db.connect()
        print("✅ Database connection successful!")
        
        # Test query
        async with db.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            print(f"✅ Query test: {result}")
            
            # Check if categories table exists
            tables = await conn.fetch(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name='categories'"
            )
            if tables:
                print("✅ Categories table exists")
                # Count categories
                count = await conn.fetchval("SELECT COUNT(*) FROM categories")
                print(f"✅ Categories count: {count}")
            else:
                print("❌ Categories table NOT found")
                print("📝 Run database migration to create tables")
                
        await db.disconnect()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    exit(0 if success else 1)
