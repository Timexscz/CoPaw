#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Integration test for version control features."""
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_skills_lock():
    """Test SkillsLockManager."""
    print("📦 Testing SkillsLockManager...")
    
    from copaw.agents.skills_lock import SkillsLockManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create manager
        manager = SkillsLockManager(tmpdir)
        
        # Test generate_lock
        lock_data = manager.generate_lock()
        assert "version" in lock_data
        assert "skills" in lock_data
        assert "generated_at" in lock_data
        
        # Test save_lock
        lock_path = manager.save_lock()
        assert Path(lock_path).exists()
        
        # Test load_lock
        loaded = manager.load_lock()
        assert loaded is not None
        assert loaded["version"] == 1
        
        # Test compare_versions
        assert SkillsLockManager._compare_versions("1.0.0", "1.0.0") == 0
        assert SkillsLockManager._compare_versions("1.0.0", "1.0.1") == -1
        assert SkillsLockManager._compare_versions("1.1.0", "1.0.9") == 1
        
        print("  ✅ SkillsLockManager: PASS")
        return True

def test_memory_version():
    """Test MemoryVersionManager."""
    print("💾 Testing MemoryVersionManager...")
    
    from copaw.agents.memory.version_manager import MemoryVersionManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        memory_dir = tmpdir / "memory"
        memory_dir.mkdir()
        
        # Create manager
        manager = MemoryVersionManager(memory_dir, max_versions=5)
        
        # Create test file
        test_file = memory_dir / "TEST.md"
        test_file.write_text("# Test\n\nContent", encoding="utf-8")
        
        # Test save_version
        version_path = manager.save_version("TEST.md")
        assert Path(version_path).exists()
        
        # Test list_versions
        versions = manager.list_versions("TEST.md")
        assert len(versions) == 1
        
        # Test modify and save again
        test_file.write_text("# Test\n\nModified content", encoding="utf-8")
        manager.save_version("TEST.md")
        
        versions = manager.list_versions("TEST.md")
        assert len(versions) == 2
        
        # Test diff
        diff = manager.diff_versions(versions[1]["path"], versions[0]["path"])
        assert isinstance(diff, str)
        assert len(diff) > 0
        
        # Test cleanup
        for i in range(10):
            manager.save_version("TEST.md")
        
        result = manager.cleanup(dry_run=True)
        assert result["deleted_count"] > 0
        assert result["kept_count"] == 5  # max_versions
        
        print("  ✅ MemoryVersionManager: PASS")
        return True

def test_mcp_version():
    """Test MCPVersionTracker."""
    print("🔗 Testing MCPVersionTracker...")
    
    from copaw.app.mcp.version_tracker import MCPVersionTracker
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create tracker
        tracker = MCPVersionTracker(tmpdir)
        
        # Test record_version
        version_info = {
            "version": "1.0.0",
            "protocol_version": "2024-11-05",
            "capabilities": {"tools": True},
        }
        tracker.record_version("test_client", version_info)
        
        # Test load
        data = tracker.load()
        assert "test_client" in data["clients"]
        assert data["clients"]["test_client"]["version"] == "1.0.0"
        
        # Test list_clients
        clients = tracker.list_clients()
        assert len(clients) == 1
        assert clients[0]["key"] == "test_client"
        
        # Test check_compatibility
        compat = tracker.check_compatibility(
            "test_client",
            {"version": "1.1.0", "capabilities": {"tools": True}},
        )
        assert "compatible" in compat
        
        # Test version history
        tracker.record_version("test_client", {"version": "2.0.0"})
        history = tracker.get_version_history("test_client")
        assert len(history) == 2
        
        # Test rollback
        result = tracker.rollback_version("test_client", "1.0.0")
        assert result["success"] is True
        
        print("  ✅ MCPVersionTracker: PASS")
        return True

def test_cli_commands():
    """Test CLI command structure."""
    print("📋 Testing CLI command structure...")
    
    cli_dir = Path(__file__).parent / "src" / "copaw" / "cli"
    
    # Check files exist
    cli_files = [
        "skills_version_cmd.py",
        "memory_version_cmd.py",
        "mcp_version_cmd.py",
    ]
    
    for filename in cli_files:
        filepath = cli_dir / filename
        assert filepath.exists(), f"Missing: {filename}"
    
    # Check main.py registration
    main_file = cli_dir / "main.py"
    content = main_file.read_text(encoding="utf-8")
    
    assert "skills_version" in content, "skills_version not registered"
    assert "memory_version" in content, "memory_version not registered"
    assert "mcp_version" in content, "mcp_version not registered"
    
    print("  ✅ CLI commands: PASS")
    return True

def main():
    """Run all integration tests."""
    print("=" * 70)
    print("CoPaw Version Control Integration Tests")
    print("=" * 70)
    print()
    
    tests = [
        ("Skills Lock", test_skills_lock),
        ("Memory Version", test_memory_version),
        ("MCP Version", test_mcp_version),
        ("CLI Commands", test_cli_commands),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"  ❌ {name}: FAIL - {e}")
        print()
    
    print("=" * 70)
    print("Test Summary:")
    print("-" * 70)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for name, result, error in results:
        if result:
            print(f"  ✅ {name}: PASS")
        else:
            print(f"  ❌ {name}: FAIL - {error}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
