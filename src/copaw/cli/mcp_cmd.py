# -*- coding: utf-8 -*-
"""CLI command: manage MCP clients."""
from __future__ import annotations

import json
import asyncio
import click
from rich.table import Table
from rich.console import Console

from ..config import load_config, save_config
from .utils import prompt_select, prompt_text, prompt_confirm
from .mcp_deps_installer import (
    check_mcp_client_dependencies,
    check_all_mcp_clients,
)
from .mcp_diagnose import diagnose_client, diagnose_all

console = Console()


@click.group()
def mcp_group():
    """Manage MCP (Model Context Protocol) clients."""
    pass


@mcp_group.command("list")
@click.option(
    "--enabled/--all",
    default=True,
    help="Show only enabled clients (default) or all clients",
)
def list_clients(enabled: bool):
    """List MCP clients."""
    config = load_config()
    
    if not config.mcp.clients:
        console.print("[yellow]No MCP clients configured.[/yellow]")
        return
    
    # Filter clients
    clients = config.mcp.clients
    if enabled:
        clients = {k: v for k, v in clients.items() if v.enabled}
    
    if not clients:
        console.print("[yellow]No enabled MCP clients.[/yellow]")
        return
    
    # Create table
    table = Table(title="MCP Clients")
    table.add_column("Key", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Status", style="blue")
    table.add_column("Description", style="dim")
    
    for key, client in sorted(clients.items()):
        # Determine type
        if client.transport in ["streamable_http", "sse"]:
            client_type = "Remote"
        else:
            client_type = "Local"
        
        status = "✓ Enabled" if client.enabled else "✗ Disabled"
        
        table.add_row(
            key,
            client.name,
            client_type,
            status,
            client.description or "-",
        )
    
    console.print(table)
    console.print(f"\nTotal: {len(clients)} client(s)")


@mcp_group.command("add")
@click.argument("key")
@click.option("--name", required=True, help="Client display name")
@click.option(
    "--type",
    "client_type",
    type=click.Choice(["local", "remote"]),
    required=True,
    help="Client type: local (stdio) or remote (HTTP/SSE)",
)
@click.option("--command", help="Command to run (for local clients)")
@click.option("--args", help="Command arguments (comma-separated)")
@click.option("--url", help="Remote URL (for remote clients)")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "streamable_http", "sse"]),
    default="stdio",
    help="Transport type",
)
@click.option("--env", help="Environment variables (KEY=VALUE,comma-separated)")
@click.option("--enabled", is_flag=True, default=True, help="Enable client after creation")
def add_client(
    key: str,
    name: str,
    client_type: str,
    command: str | None,
    args: str | None,
    url: str | None,
    transport: str,
    env: str | None,
    enabled: bool,
):
    """Add a new MCP client.
    
    \b
    Examples:
      # Add local client
      copaw mcp add my-mcp --name "My MCP" --type local \\
        --command npx --args "-y,@modelcontextprotocol/server-example"
      
      # Add remote client
      copaw mcp add remote-mcp --name "Remote MCP" --type remote \\
        --url http://localhost:8000/mcp --transport streamable_http
    """
    config = load_config()
    
    # Check if client already exists
    if key in config.mcp.clients:
        console.print(f"[red]Error: MCP client '{key}' already exists.[/red]")
        return
    
    # Validate parameters based on type
    if client_type == "local":
        if not command:
            console.print("[red]Error: --command is required for local clients.[/red]")
            return
        transport = "stdio"
    else:  # remote
        if not url:
            console.print("[red]Error: --url is required for remote clients.[/red]")
            return
        if transport not in ["streamable_http", "sse"]:
            transport = "streamable_http"
    
    # Parse arguments
    args_list = [a.strip() for a in args.split(",")] if args else []
    
    # Parse environment variables
    env_dict = {}
    if env:
        for item in env.split(","):
            if "=" in item:
                k, v = item.split("=", 1)
                env_dict[k.strip()] = v.strip()
    
    # Create client config
    from ..config.config import MCPClientConfig
    
    client_config = MCPClientConfig(
        name=name,
        description=f"{client_type.capitalize()} MCP client",
        enabled=enabled,
        transport=transport,
        url=url or "",
        headers={},
        command=command or "",
        args=args_list,
        env=env_dict,
        cwd="",
    )
    
    # Add to config and save
    config.mcp.clients[key] = client_config
    save_config(config)
    
    console.print(f"[green]✓ MCP client '{key}' added successfully![/green]")
    console.print(f"  Name: {name}")
    console.print(f"  Type: {client_type.capitalize()}")
    console.print(f"  Transport: {transport}")
    if client_type == "local":
        console.print(f"  Command: {command} {' '.join(args_list)}")
    else:
        console.print(f"  URL: {url}")


@mcp_group.command("remove")
@click.argument("key")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
def remove_client(key: str, yes: bool):
    """Remove an MCP client."""
    config = load_config()
    
    if key not in config.mcp.clients:
        console.print(f"[red]Error: MCP client '{key}' not found.[/red]")
        return
    
    if not yes:
        client = config.mcp.clients[key]
        console.print(f"About to remove MCP client:")
        console.print(f"  Key: {key}")
        console.print(f"  Name: {client.name}")
        
        if not prompt_confirm("Continue?", default=False):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return
    
    # Remove client
    del config.mcp.clients[key]
    save_config(config)
    
    console.print(f"[green]✓ MCP client '{key}' removed.[/green]")


@mcp_group.command("enable")
@click.argument("key")
def enable_client(key: str):
    """Enable an MCP client."""
    config = load_config()
    
    if key not in config.mcp.clients:
        console.print(f"[red]Error: MCP client '{key}' not found.[/red]")
        return
    
    config.mcp.clients[key].enabled = True
    save_config(config)
    
    console.print(f"[green]✓ MCP client '{key}' enabled.[/green]")


@mcp_group.command("disable")
@click.argument("key")
def disable_client(key: str):
    """Disable an MCP client."""
    config = load_config()
    
    if key not in config.mcp.clients:
        console.print(f"[red]Error: MCP client '{key}' not found.[/red]")
        return
    
    config.mcp.clients[key].enabled = False
    save_config(config)
    
    console.print(f"[green]✓ MCP client '{key}' disabled.[/green]")


@mcp_group.command("info")
@click.argument("key")
def info_client(key: str):
    """Show detailed information about an MCP client."""
    config = load_config()
    
    if key not in config.mcp.clients:
        console.print(f"[red]Error: MCP client '{key}' not found.[/red]")
        return
    
    client = config.mcp.clients[key]
    
    console.print(f"\n[cyan]=== MCP Client: {key} ===[/cyan]\n")
    console.print(f"[green]Name:[/green]        {client.name}")
    console.print(f"[green]Enabled:[/green]      {'✓ Yes' if client.enabled else '✗ No'}")
    console.print(f"[green]Type:[/green]         {'Remote' if client.transport in ['streamable_http', 'sse'] else 'Local'}")
    console.print(f"[green]Transport:[/green]    {client.transport}")
    
    if client.url:
        console.print(f"[green]URL:[/green]         {client.url}")
    
    if client.command:
        console.print(f"[green]Command:[/green]     {client.command}")
        if client.args:
            console.print(f"[green]Args:[/green]       {' '.join(client.args)}")
    
    if client.env:
        console.print(f"\n[green]Environment Variables:[/green]")
        for k, v in client.env.items():
            # Mask sensitive values
            masked_v = "****" + v[-4:] if len(v) > 4 else "****"
            console.print(f"  {k}={masked_v}")
    
    if client.cwd:
        console.print(f"[green]Working Dir:[/green] {client.cwd}")
    
    console.print()


@mcp_group.command("export")
@click.argument("output_file", type=click.Path())
@click.option("--keys", help="Export specific clients (comma-separated)")
def export_clients(output_file: str, keys: str | None):
    """Export MCP clients to JSON file."""
    config = load_config()
    
    clients = config.mcp.clients
    
    # Filter if specific keys requested
    if keys:
        key_list = [k.strip() for k in keys.split(",")]
        clients = {k: v for k, v in clients.items() if k in key_list}
    
    if not clients:
        console.print("[yellow]No clients to export.[/yellow]")
        return
    
    # Export to JSON
    export_data = {
        "mcpServers": {
            key: {
                "name": client.name,
                "description": client.description,
                "enabled": client.enabled,
                "transport": client.transport,
                "url": client.url,
                "command": client.command,
                "args": client.args,
                "env": client.env,
                "cwd": client.cwd,
            }
            for key, client in clients.items()
        }
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    console.print(f"[green]✓ Exported {len(clients)} client(s) to {output_file}[/green]")


@mcp_group.command("import")
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--enable", is_flag=True, default=True, help="Enable clients after import")
@click.option("--overwrite", is_flag=True, help="Overwrite existing clients")
def import_clients(input_file: str, enable: bool, overwrite: bool):
    """Import MCP clients from JSON file."""
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON file: {e}[/red]")
        return
    
    # Support both formats: { "mcpServers": {...} } or direct {...}
    if "mcpServers" in data:
        clients_data = data["mcpServers"]
    else:
        clients_data = data
    
    if not clients_data:
        console.print("[yellow]No clients found in file.[/yellow]")
        return
    
    config = load_config()
    imported = 0
    skipped = 0
    
    from ..config.config import MCPClientConfig
    
    for key, client_data in clients_data.items():
        # Check if client already exists
        if key in config.mcp.clients:
            if overwrite:
                console.print(f"[yellow]Overwriting existing client: {key}[/yellow]")
            else:
                console.print(f"[yellow]Skipping existing client: {key}[/yellow]")
                skipped += 1
                continue
        
        # Create client config
        client_config = MCPClientConfig(
            name=client_data.get("name", key),
            description=client_data.get("description", ""),
            enabled=enable,
            transport=client_data.get("transport", "stdio"),
            url=client_data.get("url", ""),
            headers=client_data.get("headers", {}),
            command=client_data.get("command", ""),
            args=client_data.get("args", []),
            env=client_data.get("env", {}),
            cwd=client_data.get("cwd", ""),
        )
        
        config.mcp.clients[key] = client_config
        imported += 1
        console.print(f"[green]✓ Imported: {key}[/green]")
    
    save_config(config)
    console.print(f"\n[green]✓ Imported {imported} client(s), skipped {skipped}[/green]")


@mcp_group.command("interactive")
def interactive():
    """Interactive MCP client management."""
    config = load_config()
    
    while True:
        console.print("\n[cyan]=== MCP Client Management ===[/cyan]")
        
        clients = list(config.mcp.clients.items())
        if not clients:
            console.print("[yellow]No MCP clients configured.[/yellow]")
        else:
            for i, (key, client) in enumerate(clients, 1):
                status = "✓" if client.enabled else "✗"
                client_type = "Remote" if client.transport in ["streamable_http", "sse"] else "Local"
                console.print(f"  {i}. [{status}] {key} - {client.name} ({client_type})")
        
        console.print()
        console.print("  [green]a[/green] - Add client")
        console.print("  [green]r[/green] - Remove client")
        console.print("  [green]e[/green] - Enable/Disable client")
        console.print("  [green]i[/green] - Show client info")
        console.print("  [green]q[/green] - Quit")
        
        choice = prompt_text("Choice", default="q").lower()
        
        if choice == "q":
            break
        elif choice == "a":
            # Add client
            key = prompt_text("Client key")
            if key in config.mcp.clients:
                console.print("[red]Client already exists.[/red]")
                continue
            
            name = prompt_text("Display name")
            client_type = prompt_select(
                "Type",
                choices=["local", "remote"],
                default="local",
            )
            
            if client_type == "local":
                command = prompt_text("Command (e.g., npx)")
                args_str = prompt_text("Arguments (comma-separated)", default="")
                args_list = [a.strip() for a in args_str.split(",")] if args_str else []
                url = ""
                transport = "stdio"
            else:
                command = ""
                args_list = []
                url = prompt_text("URL")
                transport = prompt_select(
                    "Transport",
                    choices=["streamable_http", "sse"],
                    default="streamable_http",
                )
            
            from ..config.config import MCPClientConfig
            
            client_config = MCPClientConfig(
                name=name,
                description="",
                enabled=True,
                transport=transport,
                url=url,
                headers={},
                command=command,
                args=args_list,
                env={},
                cwd="",
            )
            
            config.mcp.clients[key] = client_config
            save_config(config)
            console.print(f"[green]✓ Client '{key}' added.[/green]")
            
        elif choice == "r":
            if not clients:
                continue
            key = prompt_select(
                "Select client to remove",
                choices=[k for k, _ in clients],
            )
            if prompt_confirm(f"Remove {key}?", default=False):
                del config.mcp.clients[key]
                save_config(config)
                console.print(f"[green]✓ Client '{key}' removed.[/green]")
                
        elif choice == "e":
            if not clients:
                continue
            key = prompt_select(
                "Select client",
                choices=[k for k, _ in clients],
            )
            client = config.mcp.clients[key]
            new_status = not client.enabled
            client.enabled = new_status
            save_config(config)
            status_text = "enabled" if new_status else "disabled"
            console.print(f"[green]✓ Client '{key}' {status_text}.[/green]")
            
        elif choice == "i":
            if not clients:
                continue
            key = prompt_select(
                "Select client",
                choices=[k for k, _ in clients],
            )
            # Call info command
            ctx = click.get_current_context()
            ctx.invoke(info_client, key=key)
        
        else:
            console.print("[yellow]Unknown command.[/yellow]")

    console.print("[blue]Goodbye![/blue]")


@mcp_group.command("check-deps")
@click.argument("key", required=False)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Auto-confirm all installations",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Only check dependencies, don't install",
)
def check_deps(key: str | None, yes: bool, dry_run: bool):
    """Check and install MCP client dependencies.

    \b
    Examples:
      # Check all clients
      copaw mcp check-deps

      # Check specific client
      copaw mcp check-deps my-mcp

      # Dry run (no installation)
      copaw mcp check-deps --dry-run

      # Auto-confirm installations
      copaw mcp check-deps -y
    """
    config = load_config()

    if key:
        # Check specific client
        if key not in config.mcp.clients:
            console.print(f"[red]Error: MCP client '{key}' not found.[/red]")
            return

        client = config.mcp.clients[key]
        if not client.command:
            console.print(
                f"[yellow]Client '{key}' is remote (no command), skipping dependency check.[/yellow]"
            )
            return

        success = asyncio.run(
            check_mcp_client_dependencies(
                command=client.command,
                args=client.args,
                client_name=client.name,
                auto_confirm=yes,
                dry_run=dry_run,
            )
        )

        if success:
            console.print(f"\n[green]✓ Client '{key}' dependencies are satisfied.[/green]")
        else:
            console.print(
                f"\n[red]✗ Client '{key}' has missing dependencies. Some features may not work.[/red]"
            )
    else:
        # Check all clients
        clients = {
            k: v for k, v in config.mcp.clients.items() if v.enabled
        }

        if not clients:
            console.print("[yellow]No enabled MCP clients to check.[/yellow]")
            return

        results = asyncio.run(
            check_all_mcp_clients(
                clients_config=clients,
                auto_confirm=yes,
                dry_run=dry_run,
            )
        )

        failed = [k for k, v in results.items() if not v]
        if failed:
            console.print(
                f"\n[red]✗ {len(failed)} client(s) have dependency issues:[/red]"
            )
            for k in failed:
                console.print(f"  - {k}")
            raise SystemExit(1)


@mcp_group.command("install-deps")
@click.argument("key", required=False)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Auto-confirm all installations",
)
def install_deps(key: str | None, yes: bool):
    """Install missing dependencies for MCP clients.

    This is an alias for 'check-deps' that automatically confirms installations.

    \b
    Examples:
      # Install for all clients
      copaw mcp install-deps

      # Install for specific client
      copaw mcp install-deps my-mcp

      # Auto-confirm
      copaw mcp install-deps -y
    """
    # Just call check-deps with auto-confirm
    ctx = click.get_current_context()
    ctx.invoke(check_deps, key=key, yes=True)


@mcp_group.command("diagnose")
@click.argument("key", required=False)
@click.option(
    "--all",
    is_flag=True,
    help="Diagnose all remote clients",
)
def diagnose(key: str | None, all: bool):
    """Diagnose remote MCP client connection issues.

    \b
    Examples:
      # Diagnose specific client
      copaw mcp diagnose bing-cn-mcp-server

      # Diagnose all remote clients
      copaw mcp diagnose --all

    This tool helps identify:
      • Configuration issues
      • Network connectivity problems
      • MCP protocol errors
      • Server availability
    """
    import asyncio

    if key:
        asyncio.run(diagnose_client(key))
    elif all:
        asyncio.run(diagnose_all())
    else:
        console.print("[yellow]Please specify a client key or use --all[/yellow]")
        console.print("\n[cyan]Examples:[/cyan]")
        console.print("  copaw mcp diagnose bing-cn-mcp-server")
        console.print("  copaw mcp diagnose --all")
