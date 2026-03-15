#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Version control feature verification script.

This script verifies that all version control modules are properly
implemented without requiring full CoPaw dependencies.
"""
import sys
import ast
from pathlib import Path

def verify_file_syntax(filepath):
    """Verify Python file syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        return True, "OK"
    except SyntaxError as e:
        return False, str(e)

def verify_class_exists(filepath, class_name):
    """Verify that a class exists in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            # Count methods
            methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
            return True, f"Found ({len(methods)} methods)"
    return False, "Not found"

def verify_cli_commands(filepath):
    """Verify CLI commands in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count @click.command() or @group.command() decorators
    commands = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '@click.command()' in line or '.command()' in line:
            # Try to find function name
            for j in range(i, min(i+5, len(lines))):
                if 'def ' in lines[j]:
                    func_name = lines[j].split('def ')[1].split('(')[0]
                    commands.append(func_name)
                    break
    
    return commands

def main():
    """Main verification function."""
    print("=" * 60)
    print("CoPaw Version Control Feature Verification")
    print("=" * 60)
    print()
    
    # Get project root
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent
    src_dir = project_root / "src" / "copaw"
    
    # Verify core modules
    modules = [
        ("Skills Lock", "agents/skills_lock.py", "SkillsLockManager"),
        ("Memory Version", "agents/memory/version_manager.py", "MemoryVersionManager"),
        ("MCP Version", "app/mcp/version_tracker.py", "MCPVersionTracker"),
    ]
    
    print("📦 Core Modules:")
    print("-" * 60)
    
    all_ok = True
    for name, rel_path, class_name in modules:
        filepath = src_dir / rel_path
        
        if not filepath.exists():
            print(f"  ❌ {name}: File not found")
            all_ok = False
            continue
        
        # Check syntax
        syntax_ok, syntax_msg = verify_file_syntax(filepath)
        if not syntax_ok:
            print(f"  ❌ {name}: Syntax error - {syntax_msg}")
            all_ok = False
            continue
        
        # Check class exists
        class_ok, class_msg = verify_class_exists(filepath, class_name)
        if not class_ok:
            print(f"  ❌ {name}: {class_name} not found")
            all_ok = False
            continue
        
        print(f"  ✅ {name}: {class_msg}")
    
    print()
    print("📋 CLI Commands:")
    print("-" * 60)
    
    cli_files = [
        ("Skills Version", "cli/skills_version_cmd.py"),
        ("Memory Version", "cli/memory_version_cmd.py"),
        ("MCP Version", "cli/mcp_version_cmd.py"),
    ]
    
    for name, rel_path in cli_files:
        filepath = src_dir / rel_path
        
        if not filepath.exists():
            print(f"  ❌ {name}: File not found")
            all_ok = False
            continue
        
        commands = verify_cli_commands(filepath)
        if commands:
            print(f"  ✅ {name}: {len(commands)} commands")
            for cmd in commands[:5]:  # Show first 5
                print(f"      - {cmd}")
            if len(commands) > 5:
                print(f"      ... and {len(commands) - 5} more")
        else:
            print(f"  ⚠️  {name}: No commands found")
    
    print()
    print("📄 Documentation:")
    print("-" * 60)
    
    docs = [
        "docs/VERSION_CONTROL_USER_GUIDE.md",
        "docs/VERSION_CONTROL_STRATEGY_COMPARISON.md",
        "docs/SKILLS_MCP_VERSION_CONTROL_ANALYSIS.md",
        "docs/MEMORY_VERSION_MANAGEMENT_ANALYSIS.md",
    ]
    
    for doc in docs:
        docpath = project_root / doc
        if docpath.exists():
            size = docpath.stat().st_size
            print(f"  ✅ {doc}: {size} bytes")
        else:
            print(f"  ⚠️  {doc}: Not found")
    
    print()
    print("🧪 Tests:")
    print("-" * 60)
    
    test_files = [
        "tests/test_skills_lock.py",
        "tests/test_memory_version.py",
        "tests/test_mcp_version.py",
    ]
    
    for test_file in test_files:
        testpath = Path(__file__).parent / test_file
        if testpath.exists():
            # Count test functions
            with open(testpath, 'r', encoding='utf-8') as f:
                content = f.read()
            test_count = content.count('def test_')
            print(f"  ✅ {test_file}: {test_count} tests")
        else:
            print(f"  ⚠️  {test_file}: Not found")
    
    print()
    print("=" * 60)
    
    if all_ok:
        print("✅ All core modules verified successfully!")
    else:
        print("⚠️  Some modules have issues. Please review.")
    
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
