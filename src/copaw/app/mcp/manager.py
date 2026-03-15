# -*- coding: utf-8 -*-
"""MCP client manager for hot-reloadable client lifecycle management.

This module provides centralized management of MCP clients with support
for runtime updates without restarting the application.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, TYPE_CHECKING

from agentscope.mcp import HttpStatefulClient, StdIOStatefulClient

if TYPE_CHECKING:
    from ...config.config import MCPClientConfig, MCPConfig

logger = logging.getLogger(__name__)


class MCPClientManager:
    """Manages MCP clients with hot-reload support.

    This manager handles the lifecycle of MCP clients, including:
    - Initial loading from config
    - Runtime replacement when config changes
    - Cleanup on shutdown

    Design pattern mirrors ChannelManager for consistency.
    """

    def __init__(self) -> None:
        """Initialize an empty MCP client manager."""
        self._clients: Dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def init_from_config(self, config: "MCPConfig") -> None:
        """Initialize clients from configuration.

        Args:
            config: MCP configuration containing client definitions
        """
        logger.debug("Initializing MCP clients from config")
        for key, client_config in config.clients.items():
            if not client_config.enabled:
                logger.debug(f"MCP client '{key}' is disabled, skipping")
                continue

            try:
                await self._add_client(key, client_config)
                logger.debug(f"MCP client '{key}' initialized successfully")
            except BaseException as e:
                if isinstance(e, (KeyboardInterrupt, SystemExit)):
                    raise
                logger.warning(
                    f"Failed to initialize MCP client '{key}': {e}",
                    exc_info=True,
                )

    async def get_clients(self) -> List[Any]:
        """Get list of all active MCP clients.

        This method is called by the runner on each query to get
        the latest set of clients.

        Returns:
            List of connected MCP client instances
        """
        async with self._lock:
            return [
                client
                for client in self._clients.values()
                if client is not None
            ]

    async def replace_client(
        self,
        key: str,
        client_config: "MCPClientConfig",
        timeout: float = 60.0,
    ) -> None:
        """Replace or add a client with new configuration.

        Flow: connect new (outside lock) → swap + close old (inside lock).
        This ensures minimal lock holding time.

        Args:
            key: Client identifier (from config)
            client_config: New client configuration
            timeout: Connection timeout in seconds (default 60s)
        """
        # 1. Create and connect new client outside lock (may be slow)
        logger.debug(f"Connecting new MCP client: {key}")
        new_client = self._build_client(client_config)

        try:
            # Add timeout to prevent indefinite blocking
            await asyncio.wait_for(new_client.connect(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(
                f"Timeout connecting MCP client '{key}' after {timeout}s",
            )
            try:
                await new_client.close()
            except Exception:
                pass
            raise
        except Exception as e:
            logger.warning(f"Failed to connect MCP client '{key}': {e}")
            try:
                await new_client.close()
            except Exception:
                pass
            raise

        # 2. Swap and close old client inside lock
        async with self._lock:
            old_client = self._clients.get(key)
            self._clients[key] = new_client

            if old_client is not None:
                logger.debug(f"Closing old MCP client: {key}")
                try:
                    await old_client.close()
                except Exception as e:
                    logger.warning(
                        f"Error closing old MCP client '{key}': {e}",
                    )
            else:
                logger.debug(f"Added new MCP client: {key}")

    async def remove_client(self, key: str) -> None:
        """Remove and close a client.

        Args:
            key: Client identifier to remove
        """
        async with self._lock:
            old_client = self._clients.pop(key, None)

        if old_client is not None:
            logger.debug(f"Removing MCP client: {key}")
            try:
                await old_client.close()
            except Exception as e:
                logger.warning(f"Error closing MCP client '{key}': {e}")

    async def close_all(self) -> None:
        """Close all MCP clients.

        Called during application shutdown.
        """
        async with self._lock:
            clients_snapshot = list(self._clients.items())
            self._clients.clear()

        logger.debug("Closing all MCP clients")
        for key, client in clients_snapshot:
            if client is not None:
                try:
                    await client.close()
                except Exception as e:
                    logger.warning(f"Error closing MCP client '{key}': {e}")

    async def _add_client(
        self,
        key: str,
        client_config: "MCPClientConfig",
        timeout: float = 60.0,
    ) -> None:
        """Add a new client (used during initial setup).

        Args:
            key: Client identifier
            client_config: Client configuration
            timeout: Connection timeout in seconds (default 60s)
        """
        # Auto-check dependencies for stdio clients
        if client_config.transport == "stdio" and client_config.command:
            try:
                from ...cli.mcp_deps_installer import MCPDependencyInstaller
                installer = MCPDependencyInstaller(auto_confirm=False, dry_run=False)

                # Quick check without prompting (just detect missing tools)
                tool = installer.detect_command_tool(client_config.command)
                is_installed = await installer.check_tool_installed(tool)

                if not is_installed:
                    logger.warning(
                        f"MCP client '{key}' requires '{tool.value}' which is not installed. "
                        f"Run 'copaw mcp install-deps {key}' to install dependencies."
                    )
            except Exception as e:
                logger.debug(f"Dependency check failed for '{key}': {e}")

        client = self._build_client(client_config)

        # Add timeout to prevent indefinite blocking
        try:
            await asyncio.wait_for(client.connect(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(
                f"Timeout connecting MCP client '{key}' after {timeout}s. "
                f"URL: {client_config.url}, Transport: {client_config.transport}"
            )
            raise
        except Exception as e:
            # Add more context to the error
            error_type = type(e).__name__
            error_msg = str(e)

            logger.error(
                f"Failed to connect MCP client '{key}':\n"
                f"  Error Type: {error_type}\n"
                f"  Error Message: {error_msg}\n"
                f"  URL: {client_config.url}\n"
                f"  Transport: {client_config.transport}\n"
                f"  Name: {client_config.name}\n"
                f"\n"
                f"Possible causes:\n"
                f"  • Remote server is not running\n"
                f"  • Wrong URL or port\n"
                f"  • MCP protocol version mismatch\n"
                f"  • Server rejected the connection (authentication/config error)\n"
                f"  • Network/firewall issues\n"
                f"\n"
                f"Try running: python -m copaw.cli.mcp_diagnose {key}"
            )
            raise

        async with self._lock:
            self._clients[key] = client

    @staticmethod
    def _build_client(client_config: "MCPClientConfig") -> Any:
        """Build MCP client instance by configured transport."""
        rebuild_info = {
            "name": client_config.name,
            "transport": client_config.transport,
            "url": client_config.url,
            "headers": client_config.headers or None,
            "command": client_config.command,
            "args": list(client_config.args),
            "env": dict(client_config.env),
            "cwd": client_config.cwd or None,
        }

        if client_config.transport == "stdio":
            client = StdIOStatefulClient(
                name=client_config.name,
                command=client_config.command,
                args=client_config.args,
                env=client_config.env,
                cwd=client_config.cwd or None,
            )
            setattr(client, "_copaw_rebuild_info", rebuild_info)
            return client

        # For remote clients, add more detailed logging
        logger.debug(
            f"Building remote MCP client:\n"
            f"  Name: {client_config.name}\n"
            f"  Transport: {client_config.transport}\n"
            f"  URL: {client_config.url}\n"
            f"  Headers: {client_config.headers or 'none'}"
        )

        client = HttpStatefulClient(
            name=client_config.name,
            transport=client_config.transport,
            url=client_config.url,
            headers=client_config.headers or None,
        )
        setattr(client, "_copaw_rebuild_info", rebuild_info)
        return client
