#!/usr/bin/env python3
"""
CoPaw Installation Verification Script

This script checks if all required dependencies are installed correctly
and if the database module can be imported successfully.
"""

import sys
import importlib


def check_package(package_name: str, import_name: str = None) -> bool:
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name}: OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name}: NOT INSTALLED ({e})")
        return False


def main():
    print("=" * 60)
    print("CoPaw Installation Verification")
    print("=" * 60)
    print()
    
    # Core dependencies
    print("Checking core dependencies...")
    packages = [
        ("asyncpg", "asyncpg"),
        ("redis", "redis"),
        ("pydantic", "pydantic"),
        ("pydantic-settings", "pydantic_settings"),
        ("python-frontmatter", "frontmatter"),
        ("markdown", "markdown"),
        ("python-dotenv", "dotenv"),
    ]
    
    all_ok = True
    for package, import_name in packages:
        if not check_package(package, import_name):
            all_ok = False
    
    print()
    
    # Try importing database module
    print("Checking database module...")
    try:
        from copaw.db.database import db, settings, redis_settings
        print(f"✅ Database module: OK")
        print(f"   PostgreSQL: {settings.host}:{settings.port}/{settings.name}")
        print(f"   Redis: {redis_settings.host}:{redis_settings.port}")
    except Exception as e:
        print(f"❌ Database module: FAILED ({e})")
        all_ok = False
    
    print()
    
    # Try importing services
    print("Checking services...")
    try:
        from copaw.services.category_service import CategoryService
        print(f"✅ CategoryService: OK")
    except Exception as e:
        print(f"❌ CategoryService: FAILED ({e})")
        all_ok = False
    
    try:
        from copaw.services.skill_parser import SkillParser
        print(f"✅ SkillParser: OK")
    except Exception as e:
        print(f"❌ SkillParser: FAILED ({e})")
        all_ok = False
    
    print()
    
    # Try importing repositories
    print("Checking repositories...")
    try:
        from copaw.db.repositories import CategoryRepository
        print(f"✅ CategoryRepository: OK")
    except Exception as e:
        print(f"❌ CategoryRepository: FAILED ({e})")
        all_ok = False
    
    print()
    print("=" * 60)
    
    if all_ok:
        print("✅ All checks passed! CoPaw is ready to use.")
        print()
        print("Next steps:")
        print("1. Make sure PostgreSQL and Redis are running")
        print("2. Run: copaw init --defaults")
        print("3. Run: copaw app")
        return 0
    else:
        print("❌ Some checks failed. Please install missing dependencies.")
        print()
        print("To install all dependencies, run:")
        print("  pip install -e .")
        return 1


if __name__ == "__main__":
    sys.exit(main())
