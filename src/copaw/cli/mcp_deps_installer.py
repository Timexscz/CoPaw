# -*- coding: utf-8 -*-
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
"""MCP dependency auto-installer.

This module automatically detects and installs dependencies for MCP clients
based on their command type (npx, uv, uvx, python, docker, etc.).

Supported Protocol Types:
- stdio: npx, uv, uvx, python, docker, node, pip, pipx
- http: streamable_http, http (remote, no dependencies)
- sse: Server-Sent Events (remote, no dependencies)
"""

from __future__ import annotations

import asyncio
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple, Dict

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.panel import Panel
from rich.table import Table

console = Console()


class CommandTool(Enum):
    """Supported command tools for MCP clients."""

    NPX = "npx"
    UV = "uv"
    UVX = "uvx"
    PYTHON = "python"
    DOCKER = "docker"
    NODE = "node"
    PIP = "pip"
    PIPX = "pipx"
    UNKNOWN = "unknown"


class TransportType(Enum):
    """MCP transport types."""

    STDIO = "stdio"
    STREAMABLE_HTTP = "streamable_http"
    HTTP = "http"
    SSE = "sse"
    REMOTE = "remote"


@dataclass
class DependencyInfo:
    """Information about a detected dependency."""

    tool: CommandTool
    package: str
    version: Optional[str] = None
    is_installed: bool = False
    install_command: Optional[List[str]] = None


@dataclass
class CheckResult:
    """Result of a dependency check."""

    client_key: str
    client_name: str
    transport: str
    success: bool
    message: str
    missing_tools: List[CommandTool] = field(default_factory=list)
    installed_tools: List[CommandTool] = field(default_factory=list)


class MCPDependencyInstaller:
    """Automatically detects and installs MCP client dependencies."""

    # Mapping of command patterns to tool types
    COMMAND_PATTERNS = {
        "npx": CommandTool.NPX,
        "uv": CommandTool.UV,
        "uvx": CommandTool.UVX,
        "python": CommandTool.PYTHON,
        "python3": CommandTool.PYTHON,
        "docker": CommandTool.DOCKER,
        "node": CommandTool.NODE,
        "pip": CommandTool.PIP,
        "pipx": CommandTool.PIPX,
    }

    # Installation instructions for each tool
    INSTALL_INSTRUCTIONS = {
        CommandTool.NPX: {
            "package": "Node.js",
            "description": "Node.js package executor",
            "install_cmd": None,  # System install required
            "manual_url": "https://nodejs.org/",
            "check_cmd": "node --version",
        },
        CommandTool.UV: {
            "package": "uv",
            "description": "Fast Python package installer",
            "install_cmd": "curl -LsSf https://astral.sh/uv/install.sh | sh",
            "manual_url": "https://github.com/astral-sh/uv",
            "check_cmd": "uv --version",
        },
        CommandTool.UVX: {
            "package": "uv",
            "description": "Fast Python package runner",
            "install_cmd": "curl -LsSf https://astral.sh/uv/install.sh | sh",
            "manual_url": "https://github.com/astral-sh/uv",
            "check_cmd": "uvx --version",
        },
        CommandTool.PYTHON: {
            "package": "Python",
            "description": "Python interpreter",
            "install_cmd": None,  # System install required
            "manual_url": "https://python.org/",
            "check_cmd": "python --version",
        },
        CommandTool.DOCKER: {
            "package": "Docker",
            "description": "Container runtime",
            "install_cmd": None,  # System install required
            "manual_url": "https://docker.com/",
            "check_cmd": "docker --version",
        },
        CommandTool.NODE: {
            "package": "Node.js",
            "description": "JavaScript runtime",
            "install_cmd": None,  # System install required
            "manual_url": "https://nodejs.org/",
            "check_cmd": "node --version",
        },
        CommandTool.PIP: {
            "package": "pip",
            "description": "Python package installer",
            "install_cmd": f"{sys.executable} -m ensurepip --upgrade",
            "manual_url": "https://pip.pypa.io/",
            "check_cmd": "pip --version",
        },
        CommandTool.PIPX: {
            "package": "pipx",
            "description": "Python package installer for global tools",
            "install_cmd": f"{sys.executable} -m pip install pipx && {sys.executable} -m pipx ensurepath",
            "manual_url": "https://pipx.pypa.io/",
            "check_cmd": "pipx --version",
        },
    }

    def __init__(self, auto_confirm: bool = False, dry_run: bool = False):
        """Initialize the dependency installer.

        Args:
            auto_confirm: Automatically confirm installations without prompting
            dry_run: Only check and report, don't actually install
        """
        self.auto_confirm = auto_confirm
        self.dry_run = dry_run
        self.installed_tools: set = set()
        self.failed_tools: set = set()
        self.skipped_tools: set = set()

    def detect_transport_type(self, transport: str) -> TransportType:
        """Detect transport type from configuration.

        Args:
            transport: Transport string from config

        Returns:
            TransportType enum value
        """
        transport_lower = transport.lower() if transport else ""

        if transport_lower == "stdio":
            return TransportType.STDIO
        elif transport_lower in ["streamable_http", "http"]:
            return TransportType.STREAMABLE_HTTP
        elif transport_lower == "sse":
            return TransportType.SSE
        else:
            # Default based on presence of command
            return TransportType.STDIO

    def needs_dependency_check(self, transport: str, command: str) -> bool:
        """Check if a client needs dependency checking.

        Args:
            transport: Transport type
            command: Command string (empty for remote clients)

        Returns:
            True if dependency check is needed
        """
        transport_type = self.detect_transport_type(transport)

        # Remote clients (HTTP/SSE) don't need local dependencies
        if transport_type in [
            TransportType.STREAMABLE_HTTP,
            TransportType.SSE,
            TransportType.REMOTE,
        ]:
            return False

        # STDIO clients need dependencies
        if transport_type == TransportType.STDIO and command:
            return True

        return False

    def detect_command_tool(self, command: str) -> CommandTool:
        """Detect the tool type from a command string.

        Args:
            command: The command string (e.g., "npx", "python3", "/usr/bin/python")

        Returns:
            The detected CommandTool type
        """
        # Extract base command from path
        base_cmd = command.split("/")[-1].strip()

        # Check exact matches first (for uvx vs uv)
        if base_cmd == "uvx":
            return CommandTool.UVX
        
        # Check against known patterns
        for pattern, tool in self.COMMAND_PATTERNS.items():
            if base_cmd == pattern or (pattern != "uvx" and base_cmd.startswith(f"{pattern}")):
                return tool

        return CommandTool.UNKNOWN

    def extract_package_info(
        self, command: str, args: List[str]
    ) -> Tuple[str, Optional[str]]:
        """Extract package name and version from command and args.

        Args:
            command: The base command
            args: Command arguments

        Returns:
            Tuple of (package_name, version_or_none)
        """
        if not args:
            return command, None

        # For npx: npx -y @modelcontextprotocol/server-example
        # For uvx: uvx package_name
        # For python: python -m package_name
        # For pip: pip install package_name

        package = None
        version = None
        found_m_flag = False

        i = 0
        while i < len(args):
            arg = args[i]

            # Skip flags
            if arg.startswith("-"):
                # Handle -m flag for python
                if arg == "-m":
                    found_m_flag = True
                    i += 1
                    continue
                
                # Handle flags with values like "-y" or "--yes"
                if arg in ["-y", "--yes", "-q", "--quiet", "-v", "--verbose"]:
                    i += 1
                    continue
                # Handle flags with separate value like "--version 1.0.0"
                if i + 1 < len(args) and not args[i + 1].startswith("-"):
                    i += 2
                    continue
                i += 1
                continue

            # Found package candidate
            if package is None:
                # If we saw -m flag, next arg is the package
                if found_m_flag:
                    package = arg
                    found_m_flag = False
                else:
                    package = arg
                    
                # Check if version is embedded (e.g., package @1.0.0 or package==1.0.0)
                if "@" in arg and not arg.startswith("@"):
                    parts = arg.split("@", 1)
                    package = parts[0]
                    version = parts[1]
                elif "==" in arg:
                    parts = arg.split("==", 1)
                    package = parts[0]
                    version = parts[1]
                elif arg.startswith("@") and i > 0 and not args[i - 1].startswith("-"):
                    # Handle scoped packages like @org/package
                    package = f"{args[i-1]}/{arg}" if i > 0 else arg
                    i -= 1

            i += 1

        return package or command, version

    async def check_tool_installed(self, tool: CommandTool) -> bool:
        """Check if a command tool is installed.

        Args:
            tool: The CommandTool to check

        Returns:
            True if the tool is installed
        """
        tool_names = {
            CommandTool.NPX: ["npx"],
            CommandTool.UV: ["uv"],
            CommandTool.UVX: ["uvx"],
            CommandTool.PYTHON: ["python", "python3"],
            CommandTool.DOCKER: ["docker"],
            CommandTool.NODE: ["node"],
            CommandTool.PIP: ["pip", "pip3"],
            CommandTool.PIPX: ["pipx"],
        }

        for name in tool_names.get(tool, []):
            if shutil.which(name) is not None:
                return True

        return False

    async def install_tool(self, tool: CommandTool) -> bool:
        """Attempt to install a missing tool.

        Args:
            tool: The CommandTool to install

        Returns:
            True if installation succeeded
        """
        info = self.INSTALL_INSTRUCTIONS.get(tool)
        if not info:
            console.print(
                f"[yellow]⚠ No automatic installation for {tool.value}[/yellow]"
            )
            return False

        console.print(f"\n[cyan]📦 Installing {info['package']}...[/cyan]")
        console.print(f"   Description: {info['description']}")

        if self.dry_run:
            console.print(
                f"[yellow]⚠ Dry run: would install {info['package']}[/yellow]"
            )
            if info.get("install_cmd"):
                console.print(f"   Command: {info['install_cmd']}")
            else:
                console.print(
                    f"   Manual install required: Visit {info['manual_url']}"
                )
            return True

        # For system-level installs, just provide instructions
        if not info.get("install_cmd"):
            console.print(
                f"\n[yellow]⚠ {info['package']} requires manual installation:[/yellow]"
            )
            console.print(
                Panel(
                    f"[cyan]Visit: {info['manual_url']}[/cyan]\n"
                    f"\n[cyan]Or use your system package manager:[/cyan]\n"
                    f"  • macOS: [green]brew install {info['package'].lower()}[/green]\n"
                    f"  • Ubuntu/Debian: [green]sudo apt install {info['package'].lower()}[/green]\n"
                    f"  • Fedora: [green]sudo dnf install {info['package'].lower()}[/green]",
                    title=f"📦 Install {info['package']}",
                    border_style="yellow",
                )
            )
            return False

        # Try to run installation command
        try:
            result = subprocess.run(
                info["install_cmd"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                console.print(f"[green]✓ {info['package']} installed successfully[/green]")
                return True
            else:
                console.print(
                    f"[red]✗ Failed to install {info['package']}: {result.stderr}[/red]"
                )
                return False
        except subprocess.TimeoutExpired:
            console.print(f"[red]✗ Installation timeout for {info['package']}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]✗ Error installing {info['package']}: {e}[/red]")
            return False

    def get_install_command(
        self, tool: CommandTool, package: str, version: Optional[str] = None
    ) -> Optional[List[str]]:
        """Get the installation command for a package.

        Args:
            tool: The CommandTool type
            package: Package name to install
            version: Optional version specifier

        Returns:
            List of command arguments or None if no install needed
        """
        # For npx/uvx, packages are installed on-the-fly, no pre-installation needed
        if tool in [CommandTool.NPX, CommandTool.UVX]:
            return None

        if tool == CommandTool.PIP:
            cmd = [sys.executable, "-m", "pip", "install"]
            if version:
                cmd.append(f"{package}=={version}")
            else:
                cmd.append(package)
            return cmd

        if tool == CommandTool.PIPX:
            cmd = ["pipx", "install"]
            if version:
                cmd.append(f"{package}=={version}")
            else:
                cmd.append(package)
            return cmd

        return None

    async def check_and_install(
        self, command: str, args: List[str], package_name: str = ""
    ) -> bool:
        """Check and install dependencies for an MCP client.

        Args:
            command: The base command
            args: Command arguments
            package_name: Optional package name override

        Returns:
            True if all dependencies are satisfied
        """
        tool = self.detect_command_tool(command)
        package, version = self.extract_package_info(command, args)

        if package_name:
            package = package_name

        console.print(f"\n[cyan]🔍 Checking dependencies for {package}...[/cyan]")
        console.print(f"   Tool: {tool.value}")
        console.print(f"   Package: {package}")
        if version:
            console.print(f"   Version: {version}")

        # Check if tool is installed
        is_tool_installed = await self.check_tool_installed(tool)

        if not is_tool_installed:
            console.print(
                f"[yellow]⚠ Required tool '{tool.value}' is not installed[/yellow]"
            )

            if self.auto_confirm or prompt_confirm(
                f"Install {tool.value}?", default=True
            ):
                installed = await self.install_tool(tool)
                if installed:
                    self.installed_tools.add(tool)
                else:
                    self.failed_tools.add(tool)
                    return False
            else:
                self.skipped_tools.add(tool)
                console.print("[yellow]⚠ Skipping installation, MCP client may not work[/yellow]")
                return False

        # For npx/uvx, no additional package installation needed
        if tool in [CommandTool.NPX, CommandTool.UVX]:
            console.print(f"[green]✓ Dependencies satisfied for {package}[/green]")
            return True

        # For pip/pipx, check if package is installed
        if tool in [CommandTool.PIP, CommandTool.PIPX]:
            install_cmd = self.get_install_command(tool, package, version)
            if install_cmd:
                console.print(
                    f"[yellow]⚠ Package '{package}' may need installation[/yellow]"
                )
                if self.auto_confirm or prompt_confirm(
                    f"Install {package} using {tool.value}?", default=True
                ):
                    if self.dry_run:
                        console.print(
                            f"[yellow]⚠ Dry run: would run {' '.join(install_cmd)}[/yellow]"
                        )
                    else:
                        try:
                            result = subprocess.run(
                                install_cmd,
                                capture_output=True,
                                text=True,
                                timeout=120,
                            )
                            if result.returncode == 0:
                                console.print(
                                    f"[green]✓ Package '{package}' installed[/green]"
                                )
                            else:
                                console.print(
                                    f"[red]✗ Failed to install '{package}': {result.stderr}[/red]"
                                )
                                return False
                        except Exception as e:
                            console.print(
                                f"[red]✗ Error installing '{package}': {e}[/red]"
                            )
                            return False

        return True


def prompt_confirm(message: str, default: bool = False) -> bool:
    """Prompt user for confirmation.

    Args:
        message: The confirmation message
        default: Default value if user just presses Enter

    Returns:
        User's confirmation choice
    """
    default_text = "[Y/n]" if default else "[y/N]"
    response = (
        input(f"{message} {default_text}: ").strip().lower()
    )

    if not response:
        return default

    return response in ["y", "yes"]


async def check_mcp_client_dependencies(
    command: str,
    args: List[str],
    client_name: str = "",
    auto_confirm: bool = False,
    dry_run: bool = False,
) -> bool:
    """Check and install dependencies for an MCP client.

    Args:
        command: The MCP client command
        args: Command arguments
        client_name: Optional client name for display
        auto_confirm: Automatically confirm installations
        dry_run: Only check, don't install

    Returns:
        True if all dependencies are satisfied
    """
    installer = MCPDependencyInstaller(
        auto_confirm=auto_confirm, dry_run=dry_run
    )

    display_name = client_name or f"{command} {' '.join(args)}"
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]Checking dependencies for: {display_name}[/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")

    return await installer.check_and_install(command, args)


async def check_all_mcp_clients(
    clients_config: dict,
    auto_confirm: bool = False,
    dry_run: bool = False,
) -> dict:
    """Check dependencies for all MCP clients.

    Args:
        clients_config: Dictionary of MCP client configurations
        auto_confirm: Automatically confirm installations
        dry_run: Only check, don't install

    Returns:
        Dictionary with results: {client_key: bool}
    """
    installer = MCPDependencyInstaller(
        auto_confirm=auto_confirm, dry_run=dry_run
    )

    results = {}
    total = len(clients_config)
    results_list: List[CheckResult] = []

    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]Checking dependencies for {total} MCP client(s)...[/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
    ) as progress:
        check_task = progress.add_task(
            "[cyan]Checking dependencies...", total=total
        )

        for key, client_config in clients_config.items():
            progress.update(
                check_task,
                description=f"[cyan]Checking {key}...",
                advance=0,
            )

            command = getattr(client_config, "command", "")
            args = getattr(client_config, "args", [])
            name = getattr(client_config, "name", key)
            transport = getattr(client_config, "transport", "stdio")

            # Check if dependency check is needed
            if not installer.needs_dependency_check(transport, command):
                # Remote clients don't need dependency checks
                results[key] = True
                results_list.append(
                    CheckResult(
                        client_key=key,
                        client_name=name,
                        transport=transport,
                        success=True,
                        message="Remote client (no dependencies)",
                    )
                )
                progress.update(check_task, advance=1)
                continue

            success = await installer.check_and_install(
                command, args, package_name=name
            )
            results[key] = success

            result = CheckResult(
                client_key=key,
                client_name=name,
                transport=transport,
                success=success,
                message="Dependencies satisfied" if success else "Missing dependencies",
                missing_tools=list(installer.failed_tools) if not success else [],
                installed_tools=list(installer.installed_tools) if success else [],
            )
            results_list.append(result)

            if success:
                progress.update(
                    check_task,
                    description=f"[green]✓ {key}",
                    advance=1,
                )
            else:
                progress.update(
                    check_task,
                    description=f"[red]✗ {key}",
                    advance=1,
                )

    # Summary table
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    successful = sum(1 for v in results.values() if v)
    
    table = Table(title="Dependency Check Summary")
    table.add_column("Client", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Transport", style="yellow")
    table.add_column("Status", style="blue")
    table.add_column("Message", style="dim")

    for result in results_list:
        status = "✓ Ready" if result.success else "✗ Missing deps"
        table.add_row(
            result.client_key,
            result.client_name,
            result.transport,
            status,
            result.message,
        )

    console.print(table)
    console.print(f"\n[bold]Summary:[/bold] {successful}/{total} client(s) ready")

    if installer.installed_tools:
        console.print(
            f"\n[green]✓ Installed tools:[/green] {', '.join(t.value for t in installer.installed_tools)}"
        )

    if installer.failed_tools:
        console.print(
            f"\n[red]✗ Failed to install:[/red] {', '.join(t.value for t in installer.failed_tools)}"
        )
        console.print(
            "[yellow]⚠ Some clients may not work until dependencies are installed manually[/yellow]"
        )
        
        # Show detailed instructions for failed tools
        console.print("\n[yellow]Installation instructions:[/yellow]")
        for tool in installer.failed_tools:
            info = installer.INSTALL_INSTRUCTIONS.get(tool)
            if info:
                console.print(f"  • {info['package']}: {info['manual_url']}")

    if installer.skipped_tools:
        console.print(
            f"\n[yellow]⚠ Skipped:[/yellow] {', '.join(t.value for t in installer.skipped_tools)}"
        )

    console.print(f"[bold cyan]{'='*60}[/bold cyan]")

    return results


if __name__ == "__main__":
    # Example usage
    import asyncio

    async def main():
        # Test with npx command
        success = await check_mcp_client_dependencies(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-example"],
            client_name="Example MCP",
            auto_confirm=False,
        )
        print(f"Result: {success}")

    asyncio.run(main())
