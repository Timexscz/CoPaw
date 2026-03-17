# -*- coding: utf-8 -*-
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
"""CLI command: MCP version management."""
from __future__ import annotations

import asyncio
import click
from rich.table import Table
from rich.console import Console

from ..app.mcp.version_tracker import MCPVersionTracker
from ..constant import WORKING_DIR

console = Console()


@click.group()
def mcp_version():
    """MCP client version management commands."""
    pass


@mcp_version.command()
def status():
    """Show MCP client versions and health status.
    
    Displays all tracked MCP clients with their version information,
    protocol version, capabilities, and current health status.
    """
    tracker = MCPVersionTracker(WORKING_DIR)
    
    clients = tracker.list_clients()
    
    if not clients:
        click.echo(
            "⚠️  No MCP clients tracked.\n"
            "MCP clients will be tracked automatically when used."
        )
        return
    
    # Build status table
    table = Table(title="MCP Clients")
    table.add_column("Client", style="cyan")
    table.add_column("Version", style="magenta", justify="right")
    table.add_column("Protocol", style="blue", justify="right")
    table.add_column("Health", style="green")
    table.add_column("Tools", style="yellow", justify="right")
    table.add_column("Latency", style="white", justify="right")
    table.add_column("Last Updated", style="white")
    
    for client in clients:
        key = client["key"]
        version = client.get("version", "unknown")
        protocol = client.get("protocol_version", "?")
        health = client.get("health_status", "unknown")
        tools = client.get("tools_count", "-")
        latency = client.get("latency_ms", "-")
        last_updated = client.get("last_updated", "Unknown")[:16]
        
        # Health status icon
        if health == "healthy":
            health_icon = "🟢 Healthy"
        elif health == "unhealthy":
            health_icon = "🔴 Unhealthy"
        else:
            health_icon = "🟡 Unknown"
        
        table.add_row(
            key,
            version,
            protocol,
            health_icon,
            str(tools) if tools else "-",
            f"{latency}ms" if latency else "-",
            last_updated,
        )
    
    console.print(table)
    
    # Show summary
    healthy_count = sum(
        1 for c in clients if c.get("health_status") == "healthy"
    )
    click.echo(
        f"\n📊 Summary: {healthy_count}/{len(clients)} clients healthy"
    )


@mcp_version.command()
@click.argument('client_key')
def info(client_key: str):
    """Show detailed information for an MCP client.
    
    CLIENT_KEY: Client identifier (e.g., tavily_search).
    """
    tracker = MCPVersionTracker(WORKING_DIR)
    
    client_info = tracker.get_client_info(client_key)
    
    if not client_info:
        click.echo(f"⚠️  Client '{client_key}' not found in tracker.")
        return
    
    click.echo(f"\n📋 MCP Client Information: {client_key}\n")
    
    click.echo(f"Version: {client_info.get('version', 'unknown')}")
    click.echo(
        f"Protocol Version: "
        f"{client_info.get('protocol_version', 'unknown')}"
    )
    click.echo(
        f"Health Status: {client_info.get('health_status', 'unknown')}"
    )
    click.echo(
        f"Last Updated: {client_info.get('last_updated', 'unknown')}"
    )
    
    # Show capabilities
    capabilities = client_info.get("capabilities", {})
    if capabilities:
        click.echo("\nCapabilities:")
        for cap, value in capabilities.items():
            status = "✓" if value else "✗"
            click.echo(f"   {status} {cap}")
    
    # Show version history
    version_history = client_info.get("version_history", [])
    if version_history:
        click.echo(f"\nVersion History ({len(version_history)} entries):")
        for record in version_history[-5:]:  # Show last 5
            version = record.get("version", "?")
            timestamp = record.get("timestamp", "?")[:16]
            click.echo(f"   - v{version} ({timestamp})")
    
    # Show health history
    health_history = client_info.get("health_history", [])
    if health_history:
        click.echo(
            f"\nHealth History ({len(health_history)} checks):"
        )
        last_check = health_history[-1] if health_history else {}
        status = last_check.get("status", "?")
        latency = last_check.get("latency_ms", "-")
        click.echo(
            f"   Last: {status}, Latency: {latency}ms"
        )


@mcp_version.command()
@click.argument('client_key')
async def check(client_key: str):
    """Check for MCP server updates.
    
    CLIENT_KEY: Client identifier.
    
    Note: This is a placeholder for future implementation.
    MCP version checking depends on server implementation.
    """
    tracker = MCPVersionTracker(WORKING_DIR)
    
    client_info = tracker.get_client_info(client_key)
    
    if not client_info:
        click.echo(f"⚠️  Client '{client_key}' not found in tracker.")
        return
    
    click.echo(f"🔍 Checking updates for {client_key}...")
    
    # TODO: Implement actual version checking logic
    # This requires MCP server to expose version information
    
    click.echo(
        "⚠️  Version check not yet implemented for this client.\n"
        "Feature coming soon."
    )


@mcp_version.command()
@click.argument('client_key')
@click.argument('target_version')
@click.option(
    '--yes',
    is_flag=True,
    help='Skip confirmation prompt.',
)
def rollback(client_key: str, target_version: str, yes: bool):
    """Rollback MCP client to a previous version.
    
    CLIENT_KEY: Client identifier.
    TARGET_VERSION: Version to rollback to.
    """
    tracker = MCPVersionTracker(WORKING_DIR)
    
    client_info = tracker.get_client_info(client_key)
    
    if not client_info:
        click.echo(f"⚠️  Client '{client_key}' not found in tracker.")
        return
    
    # Show current version
    current_version = client_info.get("version", "unknown")
    click.echo(f"\n📋 Rollback Information:\n")
    click.echo(f"Client: {client_key}")
    click.echo(f"Current Version: {current_version}")
    click.echo(f"Target Version: {target_version}")
    
    if not yes:
        if not click.confirm(
            "\n⚠️  This will update the tracker record.\n"
            "You need to reconfigure the client manually.\n"
            "Continue?"
        ):
            click.echo("Rollback cancelled.")
            return
    
    result = tracker.rollback_version(client_key, target_version)
    
    if result.get("success"):
        click.echo(f"✅ Rolled back {client_key}:")
        click.echo(
            f"   {result['from_version']} → "
            f"{result['to_version']}"
        )
        click.echo(
            "\n💡 Note: You need to manually reconfigure the "
            "client to apply the rollback."
        )
    else:
        click.echo(f"❌ Failed: {result.get('error', 'Unknown error')}")


@mcp_version.command()
@click.option(
    '--interval',
    default=60,
    help='Health check interval in seconds.',
)
@click.option(
    '--timeout',
    default=10,
    help='Health check timeout in seconds.',
)
def health_check(interval: int, timeout: int):
    """Run health checks on all MCP clients.
    
    Performs immediate health checks on all tracked clients.
    """
    tracker = MCPVersionTracker(
        WORKING_DIR,
        health_check_interval=interval,
    )
    
    click.echo(
        f"🏥 Running health checks "
        f"(timeout: {timeout}s)...\n"
    )
    
    # This is a simplified version
    # Full implementation would require actual client instances
    
    clients = tracker.list_clients()
    
    if not clients:
        click.echo("⚠️  No MCP clients to check.")
        return
    
    # TODO: Implement actual health checks with client instances
    click.echo("⚠️  Health check requires running MCP clients.\n")
    click.echo(
        "Health checks are performed automatically when MCP "
        "clients are active."
    )


@mcp_version.command()
def info():
    """Show MCP version tracker information."""
    tracker = MCPVersionTracker(WORKING_DIR)
    
    click.echo("\n📊 MCP Version Tracker Information\n")
    click.echo(f"Tracker File: {tracker.tracker_file}")
    click.echo(
        f"Health Check Interval: {tracker.health_check_interval}s"
    )
    
    data = tracker.load()
    click.echo(f"Total Clients Tracked: {len(data.get('clients', {}))}")
    click.echo(
        f"Tracker Version: {data.get('version', 1)}"
    )
