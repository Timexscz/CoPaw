#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script for MCP dependency auto-installer."""

import asyncio
import sys

sys.path.insert(0, 'src')

from copaw.cli.mcp_deps_installer import (
    MCPDependencyInstaller,
    CommandTool,
    TransportType,
    check_mcp_client_dependencies,
)


async def test_detection():
    """Test command and transport detection."""
    print("\n" + "="*60)
    print("Testing Command Detection")
    print("="*60 + "\n")
    
    installer = MCPDependencyInstaller(auto_confirm=False, dry_run=True)
    
    # Test cases
    test_cases = [
        # (command, args, expected_tool, expected_package)
        ("npx", ["-y", "@modelcontextprotocol/server"], CommandTool.NPX, "@modelcontextprotocol/server"),
        ("uvx", ["mcp-server"], CommandTool.UVX, "mcp-server"),
        ("python", ["-m", "mcp_server"], CommandTool.PYTHON, "mcp_server"),
        ("docker", ["run", "mcp/server"], CommandTool.DOCKER, "mcp/server"),
        ("node", ["server.js"], CommandTool.NODE, "server.js"),
        ("pip", ["install", "mcp-server"], CommandTool.PIP, "mcp-server"),
        ("/usr/bin/python3", ["-m", "package"], CommandTool.PYTHON, "package"),
    ]
    
    for command, args, expected_tool, expected_package in test_cases:
        tool = installer.detect_command_tool(command)
        package, version = installer.extract_package_info(command, args)
        
        tool_status = "✓" if tool == expected_tool else "✗"
        print(f"{tool_status} Command: {command:20s} → Tool: {tool.value:10s} (Expected: {expected_tool.value})")
        print(f"  Package: {package} (Version: {version})")
    
    print("\n" + "="*60)
    print("Testing Transport Detection")
    print("="*60 + "\n")
    
    transport_tests = [
        ("stdio", True),
        ("streamable_http", False),
        ("http", False),
        ("sse", False),
    ]
    
    for transport, should_check in transport_tests:
        needs_check = installer.needs_dependency_check(transport, "npx")
        status = "✓" if needs_check == should_check else "✗"
        print(f"{status} Transport: {transport:20s} → Needs check: {needs_check} (Expected: {should_check})")
    
    print("\n" + "="*60)
    print("Testing Tool Installation Check")
    print("="*60 + "\n")
    
    # Check which tools are installed
    tools_to_check = [
        CommandTool.NPX,
        CommandTool.UV,
        CommandTool.UVX,
        CommandTool.PYTHON,
        CommandTool.DOCKER,
        CommandTool.PIP,
    ]
    
    for tool in tools_to_check:
        is_installed = await installer.check_tool_installed(tool)
        status = "✓" if is_installed else "✗"
        print(f"{status} {tool.value:10s}: {'Installed' if is_installed else 'Not installed'}")
    
    print("\n" + "="*60)
    print("Testing Dependency Check (Dry Run)")
    print("="*60 + "\n")
    
    # Test with a real example (dry run)
    test_command = "npx"
    test_args = ["-y", "@modelcontextprotocol/server-example"]
    
    print(f"Testing: {test_command} {' '.join(test_args)}")
    result = await check_mcp_client_dependencies(
        command=test_command,
        args=test_args,
        client_name="Test MCP",
        auto_confirm=False,
        dry_run=True,
    )
    
    print(f"\nResult: {'Success ✓' if result else 'Failed ✗'}")
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_detection())
