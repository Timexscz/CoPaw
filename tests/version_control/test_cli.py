#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test CLI commands without full CoPaw dependencies."""
import sys
import ast
from pathlib import Path

def extract_cli_commands(filepath):
    """Extract CLI command definitions from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    commands = []
    current_command = None
    
    for node in ast.walk(tree):
        # Find function definitions with decorators
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Attribute):
                        if decorator.func.attr == 'command':
                            commands.append(node.name)
    
    return commands

def verify_cli_file(filepath, expected_commands):
    """Verify a CLI file has expected commands."""
    if not Path(filepath).exists():
        return False, f"File not found: {filepath}"
    
    commands = extract_cli_commands(filepath)
    
    if len(commands) < len(expected_commands):
        return False, f"Expected {len(expected_commands)} commands, found {len(commands)}"
    
    # Check if all expected commands are present
    missing = set(expected_commands) - set(commands)
    if missing:
        return False, f"Missing commands: {missing}"
    
    return True, f"OK - {len(commands)} commands: {', '.join(commands)}"

def main():
    """Main test function."""
    print("=" * 70)
    print("CoPaw Version Control CLI Verification")
    print("=" * 70)
    print()
    
    # Use absolute path
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent
    src_dir = project_root / "src" / "copaw" / "cli"
    
    print(f"Checking CLI files in: {src_dir}")
    print()
    
    # Define expected commands for each CLI file
    cli_files = [
        (
            "skills_version_cmd.py",
            ["lock", "status", "update", "history", "info", "diff"]
        ),
        (
            "memory_version_cmd.py",
            ["save", "list", "restore", "diff", "diff_current", "cleanup", "info"]
        ),
        (
            "mcp_version_cmd.py",
            ["status", "info", "check", "rollback", "health_check"]
        ),
    ]
    
    all_ok = True
    
    for filename, expected_commands in cli_files:
        filepath = src_dir / filename
        print(f"📋 {filename}:")
        print("-" * 70)
        
        ok, message = verify_cli_file(filepath, expected_commands)
        
        if ok:
            print(f"  ✅ {message}")
        else:
            print(f"  ❌ {message}")
            all_ok = False
        
        print()
    
    # Verify main.py registration
    print("📋 main.py registration:")
    print("-" * 70)
    
    main_file = src_dir / "main.py"
    if main_file.exists():
        content = main_file.read_text(encoding='utf-8')
        
        checks = [
            ("skills_version", "skills_version command registered"),
            ("memory_version", "memory_version command registered"),
            ("mcp_version", "mcp_version command registered"),
        ]
        
        for check_str, description in checks:
            if check_str in content:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}")
                all_ok = False
    else:
        print("  ❌ main.py not found")
        all_ok = False
    
    print()
    print("=" * 70)
    
    if all_ok:
        print("✅ All CLI commands verified successfully!")
        print()
        print("📝 Note: Full CLI testing requires CoPaw dependencies.")
        print("   Run 'copaw --help' after installing dependencies.")
    else:
        print("⚠️  Some CLI commands have issues.")
    
    print("=" * 70)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
