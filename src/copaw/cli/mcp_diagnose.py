#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MCP remote client connection diagnostic tool.

This tool helps diagnose remote MCP client connection issues.
"""

import asyncio
import sys
import json
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from copaw.config import load_config
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


async def test_http_connection(url: str, transport: str) -> bool:
    """Test HTTP/SSE connection to remote MCP server."""
    import httpx
    
    console.print(f"\n[cyan]Testing connection to: {url}[/cyan]")
    console.print(f"[cyan]Transport type: {transport}[/cyan]")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if transport == "sse":
                # For SSE, check /events endpoint
                response = await client.get(url)
            else:
                # For streamable_http, check MCP endpoint
                response = await client.get(url.rstrip("/") + "/")
            
            console.print(f"Status Code: {response.status_code}")
            
            if response.status_code in [200, 204, 405]:
                console.print("[green]✓ Server is reachable[/green]")
                return True
            elif response.status_code == 404:
                console.print("[yellow]⚠ Endpoint not found (404)[/yellow]")
                return False
            elif response.status_code >= 500:
                console.print("[red]✗ Server error[/red]")
                return False
            else:
                console.print(f"[yellow]⚠ Unexpected status: {response.status_code}[/yellow]")
                return True
                
    except httpx.ConnectError as e:
        console.print(f"[red]✗ Connection failed: {e}[/red]")
        return False
    except httpx.TimeoutException as e:
        console.print(f"[red]✗ Connection timeout: {e}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


async def test_mcp_initialize(client_key: str, client_config) -> bool:
    """Test MCP client initialization."""
    from agentscope.mcp import HttpStatefulClient
    
    console.print(f"\n[cyan]Testing MCP initialization for: {client_key}[/cyan]")
    
    try:
        client = HttpStatefulClient(
            name=client_config.name,
            transport=client_config.transport,
            url=client_config.url,
            headers=client_config.headers or None,
        )
        
        console.print("[yellow]Attempting to connect...[/yellow]")
        await client.connect()
        
        console.print("[green]✓ MCP connection successful![/green]")
        
        # Try to list tools if connected
        try:
            tools = await client.list_tools()
            console.print(f"[green]Available tools: {len(tools)}[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠ Could not list tools: {e}[/yellow]")
        
        await client.close()
        return True
        
    except Exception as e:
        console.print(f"[red]✗ MCP connection failed: {e}[/red]")
        console.print(f"[red]Error type: {type(e).__name__}[/red]")
        
        # Try to get more details
        error_str = str(e)
        if "Session terminated" in error_str:
            console.print(Panel(
                "[yellow]Session terminated during initialize phase.\n\n"
                "Possible causes:\n"
                "• MCP protocol version mismatch\n"
                "• Server rejected the connection\n"
                "• Authentication required but not provided\n"
                "• Server configuration error[/yellow]",
                title="Diagnosis",
                border_style="yellow",
            ))
        elif "Connection refused" in error_str:
            console.print(Panel(
                "[yellow]Connection refused.\n\n"
                "Possible causes:\n"
                "• Server is not running\n"
                "• Wrong URL or port\n"
                "• Firewall blocking connection[/yellow]",
                title="Diagnosis",
                border_style="yellow",
            ))
        
        return False


def check_config(client_key: str, client_config) -> bool:
    """Check if client configuration is valid."""
    console.print(f"\n[cyan]Checking configuration for: {client_key}[/cyan]")
    
    issues = []
    
    # Check transport type
    if client_config.transport not in ["stdio", "streamable_http", "sse", "http"]:
        issues.append(f"Invalid transport: {client_config.transport}")
    
    # For remote clients
    if client_config.transport in ["streamable_http", "sse", "http"]:
        if not client_config.url:
            issues.append("Remote client requires a URL")
        elif not client_config.url.startswith(("http://", "https://")):
            issues.append(f"URL should start with http:// or https://: {client_config.url}")
        
        if client_config.command:
            issues.append("Remote client should not have a command")
    
    # For local clients
    if client_config.transport == "stdio":
        if not client_config.command:
            issues.append("Local client requires a command")
    
    if issues:
        console.print("[red]Configuration issues found:[/red]")
        for issue in issues:
            console.print(f"  • {issue}")
        return False
    else:
        console.print("[green]✓ Configuration looks good[/green]")
        return True


async def diagnose_client(client_key: str):
    """Run full diagnostic for a specific client."""
    config = load_config()
    
    if client_key not in config.mcp.clients:
        console.print(f"[red]Client '{client_key}' not found![/red]")
        return
    
    client_config = config.mcp.clients[client_key]
    
    console.print(Panel(
        f"[bold]MCP Client Diagnostic: {client_key}[/bold]\n\n"
        f"Name: {client_config.name}\n"
        f"Enabled: {client_config.enabled}\n"
        f"Transport: {client_config.transport}\n"
        f"URL: {client_config.url or 'N/A'}\n"
        f"Command: {client_config.command or 'N/A'}",
        title="Client Info",
        border_style="cyan",
    ))
    
    # Step 1: Check configuration
    config_ok = check_config(client_key, client_config)
    
    if not config_ok:
        console.print("[yellow]⚠ Fix configuration issues first[/yellow]")
        return
    
    # Step 2: Test HTTP connectivity (for remote clients)
    if client_config.transport in ["streamable_http", "sse", "http"]:
        http_ok = await test_http_connection(client_config.url, client_config.transport)
        
        if not http_ok:
            console.print("[yellow]⚠ Server is not reachable, skipping MCP test[/yellow]")
            return
    
    # Step 3: Test MCP initialization
    mcp_ok = await test_mcp_initialize(client_key, client_config)
    
    # Summary
    console.print("\n" + "="*60)
    console.print("[bold]Diagnostic Summary[/bold]")
    console.print("="*60)
    
    table = Table()
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="green")
    
    table.add_row("Configuration", "✓ Pass" if config_ok else "✕ Fail")
    
    if client_config.transport in ["streamable_http", "sse", "http"]:
        table.add_row("HTTP Connectivity", "✓ Pass" if http_ok else "✕ Fail")
    
    table.add_row("MCP Initialize", "✓ Pass" if mcp_ok else "✕ Fail")
    
    console.print(table)
    
    if mcp_ok:
        console.print("\n[green]✓ All checks passed![/green]")
    else:
        console.print("\n[red]✗ MCP connection failed. Check the errors above.[/red]")
        console.print("\n[yellow]Suggestions:[/yellow]")
        console.print("  1. Verify the remote MCP server is running")
        console.print("  2. Check server logs for error messages")
        console.print("  3. Verify MCP protocol version compatibility")
        console.print("  4. Check if authentication is required")
        console.print("  5. Try accessing the URL from a browser or curl")


async def diagnose_all():
    """Run diagnostic for all remote clients."""
    config = load_config()
    
    remote_clients = {
        k: v for k, v in config.mcp.clients.items()
        if v.transport in ["streamable_http", "sse", "http"]
    }
    
    if not remote_clients:
        console.print("[yellow]No remote MCP clients configured.[/yellow]")
        return
    
    console.print(f"[cyan]Found {len(remote_clients)} remote client(s)[/cyan]")
    
    results = {}
    for key in remote_clients:
        try:
            result = await diagnose_client(key)
            results[key] = "tested"
        except Exception as e:
            console.print(f"[red]Error testing {key}: {e}[/red]")
            results[key] = f"error: {e}"
    
    console.print("\n[bold]Results:[/bold]")
    for key, result in results.items():
        status = "✓" if result == "tested" else "✗"
        console.print(f"  {status} {key}: {result}")


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Remote Client Diagnostic Tool")
    parser.add_argument(
        "client_key",
        nargs="?",
        help="Specific client key to diagnose (optional, tests all if not provided)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Test all remote clients",
    )
    
    args = parser.parse_args()
    
    console.print("[bold cyan]MCP Remote Client Diagnostic Tool[/bold cyan]")
    console.print("="*60)
    
    if args.client_key:
        await diagnose_client(args.client_key)
    elif args.all:
        await diagnose_all()
    else:
        # Default: show help
        console.print("\n[yellow]Usage:[/yellow]")
        console.print("  python -m copaw.cli.mcp_diagnose [client_key]  - Test specific client")
        console.print("  python -m copaw.cli.mcp_diagnose --all         - Test all remote clients")
        console.print("\n[cyan]Example:[/cyan]")
        console.print("  python -m copaw.cli.mcp_diagnose bing-cn-mcp-server")


if __name__ == "__main__":
    asyncio.run(main())
