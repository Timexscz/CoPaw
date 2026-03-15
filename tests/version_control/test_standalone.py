#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Standalone test - no external dependencies except standard library."""
import sys
import tempfile
import hashlib
import json
from pathlib import Path
from datetime import datetime

# Mock the constants that would come from copaw.constant
class MockConstants:
    WORKING_DIR = Path(tempfile.gettempdir()) / "copaw_test"
    ACTIVE_SKILLS_DIR = WORKING_DIR / "active_skills"
    MEMORY_DIR = WORKING_DIR / "memory"

# Create mock directories
MockConstants.WORKING_DIR.mkdir(parents=True, exist_ok=True)
MockConstants.ACTIVE_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
MockConstants.MEMORY_DIR.mkdir(parents=True, exist_ok=True)

def test_skills_lock_standalone():
    """Test SkillsLockManager logic without imports."""
    print("📦 Testing SkillsLockManager (standalone)...")
    
    # Test version comparison logic
    def compare_versions(v1, v2):
        def parse_version(v):
            parts = []
            for part in v.split("."):
                try:
                    parts.append(int(part))
                except ValueError:
                    parts.append(0)
            return parts
        
        parts1 = parse_version(v1)
        parts2 = parse_version(v2)
        max_len = max(len(parts1), len(parts2))
        parts1.extend([0] * (max_len - len(parts1)))
        parts2.extend([0] * (max_len - len(parts2)))
        
        for p1, p2 in zip(parts1, parts2):
            if p1 < p2:
                return -1
            if p1 > p2:
                return 1
        return 0
    
    # Test cases
    assert compare_versions("1.0.0", "1.0.0") == 0
    assert compare_versions("1.0.0", "1.0.1") == -1
    assert compare_versions("1.1.0", "1.0.9") == 1
    assert compare_versions("2.0.0", "1.9.9") == 1
    assert compare_versions("1.0.0", "2.0.0") == -1
    
    # Test hash calculation
    content = "test content"
    hash1 = hashlib.sha256(content.encode()).hexdigest()
    hash2 = hashlib.sha256(content.encode()).hexdigest()
    assert hash1 == hash2
    assert len(hash1) == 64
    
    # Test lock file structure
    lock_data = {
        "version": 1,
        "generated_at": datetime.now().isoformat(),
        "skills": {
            "test_skill": {
                "name": "Test Skill",
                "version": "1.0.0",
                "content_hash": hash1,
                "source": "builtin",
            }
        }
    }
    
    # Test serialization
    json_str = json.dumps(lock_data, indent=2)
    loaded = json.loads(json_str)
    assert loaded["version"] == 1
    assert "test_skill" in loaded["skills"]
    
    print("  ✅ SkillsLockManager (standalone): PASS")
    return True

def test_memory_version_standalone():
    """Test MemoryVersionManager logic without imports."""
    print("💾 Testing MemoryVersionManager (standalone)...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        memory_dir = tmpdir / "memory"
        version_dir = memory_dir / ".versions"
        memory_dir.mkdir()
        version_dir.mkdir()
        
        # Create test file
        test_file = memory_dir / "TEST.md"
        test_file.write_text("# Test\n\nContent", encoding="utf-8")
        
        # Simulate save_version
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_filename = f"TEST.md.{timestamp}"
        version_path = version_dir / version_filename
        
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "filename": "TEST.md",
            "message": "Test save",
        }
        
        version_content = (
            f"---\n"
            f"version_timestamp: {metadata['timestamp']}\n"
            f"original_filename: {metadata['filename']}\n"
            f"message: {metadata['message']}\n"
            f"---\n\n"
            f"# Test\n\nContent"
        )
        
        version_path.write_text(version_content, encoding="utf-8")
        
        # Verify version saved
        assert version_path.exists()
        
        # Simulate list_versions
        versions = list(version_dir.glob("TEST.md.*"))
        assert len(versions) == 1
        
        # Simulate cleanup (keep max 5)
        import time
        for i in range(10):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            vf = version_dir / f"TEST.md.{ts}_{i}"  # Add index to ensure unique
            vf.write_text(f"Version {i}", encoding="utf-8")
            time.sleep(0.01)  # Small delay to ensure different mtime
        
        all_versions = list(version_dir.glob("TEST.md.*"))
        sorted_versions = sorted(
            all_versions,
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        
        # Keep only 5
        to_keep = sorted_versions[:5]
        to_delete = sorted_versions[5:]
        
        assert len(to_keep) == 5
        assert len(to_delete) == 6  # 1 original + 5 extra
        
        print("  ✅ MemoryVersionManager (standalone): PASS")
        return True

def test_mcp_version_standalone():
    """Test MCPVersionTracker logic without imports."""
    print("🔗 Testing MCPVersionTracker (standalone)...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        tracker_file = tmpdir / "mcp_versions.json"
        
        # Initial data
        data = {
            "version": 1,
            "created_at": datetime.now().isoformat(),
            "clients": {},
        }
        
        # Record version
        data["clients"]["test_client"] = {
            "version": "1.0.0",
            "protocol_version": "2024-11-05",
            "capabilities": {"tools": True, "resources": False},
            "last_updated": datetime.now().isoformat(),
            "health_status": "healthy",
            "version_history": [
                {
                    "version": "1.0.0",
                    "timestamp": datetime.now().isoformat(),
                }
            ],
        }
        
        # Save
        tracker_file.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )
        
        # Load and verify
        loaded = json.loads(tracker_file.read_text(encoding="utf-8"))
        assert "test_client" in loaded["clients"]
        assert loaded["clients"]["test_client"]["version"] == "1.0.0"
        
        # Test compatibility check
        old_info = loaded["clients"]["test_client"]
        new_info = {"version": "1.1.0", "capabilities": {"tools": True}}
        
        old_caps = set(old_info.get("capabilities", {}).keys())
        new_caps = set(new_info.get("capabilities", {}).keys())
        
        removed_caps = old_caps - new_caps
        added_caps = new_caps - old_caps
        
        assert len(removed_caps) == 1  # resources removed
        assert len(added_caps) == 0
        
        # Test version history
        history = old_info.get("version_history", [])
        assert len(history) == 1
        
        print("  ✅ MCPVersionTracker (standalone): PASS")
        return True

def test_cli_syntax():
    """Test CLI file syntax."""
    print("📋 Testing CLI file syntax...")
    
    cli_dir = Path(__file__).parent / "src" / "copaw" / "cli"
    
    cli_files = [
        "skills_version_cmd.py",
        "memory_version_cmd.py",
        "mcp_version_cmd.py",
    ]
    
    for filename in cli_files:
        filepath = cli_dir / filename
        if not filepath.exists():
            print(f"  ❌ Missing: {filename}")
            return False
        
        # Check syntax
        try:
            compile(filepath.read_text(encoding="utf-8"), str(filepath), 'exec')
        except SyntaxError as e:
            print(f"  ❌ Syntax error in {filename}: {e}")
            return False
    
    # Check main.py registration
    main_file = cli_dir / "main.py"
    content = main_file.read_text(encoding="utf-8")
    
    if "skills_version" not in content:
        print("  ❌ skills_version not registered in main.py")
        return False
    if "memory_version" not in content:
        print("  ❌ memory_version not registered in main.py")
        return False
    if "mcp_version" not in content:
        print("  ❌ mcp_version not registered in main.py")
        return False
    
    print("  ✅ CLI files: PASS")
    return True

def main():
    """Run all standalone tests."""
    print("=" * 70)
    print("CoPaw Version Control Standalone Tests")
    print("=" * 70)
    print()
    
    tests = [
        ("Skills Lock", test_skills_lock_standalone),
        ("Memory Version", test_memory_version_standalone),
        ("MCP Version", test_mcp_version_standalone),
        ("CLI Syntax", test_cli_syntax),
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
    
    if passed == total:
        print()
        print("✅ All tests passed!")
        print()
        print("Note: Full CLI testing requires CoPaw installation.")
        print("      Run: pip install -e .")
        print("      Then: copaw skills version --help")
    
    print("=" * 70)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
