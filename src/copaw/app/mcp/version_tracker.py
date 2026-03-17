# -*- coding: utf-8 -*-
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
"""MCP version tracker for CoPaw.

This module provides version tracking and health monitoring for MCP clients,
enabling users to track client versions, check compatibility, and monitor
health status.

Key Features:
    - Track MCP client versions and capabilities
    - Health check monitoring
    - Compatibility checking
    - Version history tracking
    - Automatic health checks
"""
import asyncio
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Lazy import to avoid circular dependency
def _get_working_dir():
    from ...constant import WORKING_DIR
    return WORKING_DIR

logger = logging.getLogger(__name__)


class MCPVersionTracker:
    """MCP client version tracker.
    
    Tracks version information and health status for MCP clients with:
    - Version recording and history
    - Health check monitoring
    - Compatibility checking
    - Automatic cleanup
    
    Attributes:
        tracker_file: Path to mcp_versions.json file
        working_dir: Working directory path
        health_check_results: Current health check results
    """
    
    def __init__(
        self,
        working_dir: Optional[Path] = None,
        health_check_interval: int = 300,  # 5 minutes
    ):
        """Initialize MCPVersionTracker.
        
        Args:
            working_dir: Working directory path. Defaults to WORKING_DIR.
            health_check_interval: Interval between health checks in seconds.
        """
        self.working_dir = working_dir or _get_working_dir()
        self.tracker_file = self.working_dir / "mcp_versions.json"
        self.health_check_interval = health_check_interval
        self.health_check_results: Dict[str, Any] = {}
        self._health_check_task: Optional[asyncio.Task] = None
        self._clients: Dict[str, Any] = {}
        
        # Ensure working directory exists
        self.working_dir.mkdir(parents=True, exist_ok=True)
    
    def record_version(
        self,
        client_key: str,
        version_info: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record MCP client version information.
        
        Args:
            client_key: Client identifier (e.g., "tavily_search").
            version_info: Version information dict with keys:
                - version: Client version string
                - protocol_version: MCP protocol version
                - capabilities: Dict of client capabilities
            config: Optional client configuration for hashing.
        """
        data = self.load()
        
        # Calculate config hash if provided
        config_hash = ""
        if config:
            config_hash = self._hash_config(config)
        
        # Record version information
        data["clients"][client_key] = {
            "version": version_info.get("version", "unknown"),
            "protocol_version": version_info.get(
                "protocol_version", "unknown"
            ),
            "capabilities": version_info.get("capabilities", {}),
            "last_updated": datetime.now().isoformat(),
            "config_hash": config_hash,
            "health_status": "unknown",
            "health_check_count": 0,
            "last_health_check": None,
            "version_history": self._append_to_history(
                data["clients"].get(client_key, {}),
                version_info,
            ),
        }
        
        self.save(data)
        logger.info(
            f"Recorded version for {client_key}: "
            f"v{version_info.get('version', '?')} "
            f"(protocol: {version_info.get('protocol_version', '?')})"
        )
    
    def load(self) -> Dict[str, Any]:
        """Load version tracker data from file.
        
        Returns:
            Tracker data dictionary.
        """
        if not self.tracker_file.exists():
            return {
                "version": 1,
                "created_at": datetime.now().isoformat(),
                "clients": {},
            }
        
        try:
            content = self.tracker_file.read_text(encoding="utf-8")
            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to load version tracker: {e}")
            return {
                "version": 1,
                "clients": {},
            }
    
    def save(self, data: Dict[str, Any]) -> None:
        """Save version tracker data to file.
        
        Args:
            data: Tracker data dictionary.
        """
        try:
            self.tracker_file.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"Failed to save version tracker: {e}")
    
    def check_compatibility(
        self,
        client_key: str,
        new_version_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Check version compatibility for a client.
        
        Args:
            client_key: Client identifier.
            new_version_info: New version information to check.
            
        Returns:
            Compatibility check result:
            {
                "compatible": bool,
                "issues": [...],
                "warnings": [...]
            }
        """
        data = self.load()
        old_info = data["clients"].get(client_key, {})
        
        issues = []
        warnings = []
        
        # Check protocol version compatibility
        old_protocol = old_info.get("protocol_version", "")
        new_protocol = new_version_info.get("protocol_version", "")
        
        if old_protocol and old_protocol != new_protocol:
            issues.append({
                "type": "protocol_mismatch",
                "old": old_protocol,
                "new": new_protocol,
                "severity": "warning",
                "message": (
                    f"MCP protocol version changed from "
                    f"{old_protocol} to {new_protocol}"
                ),
            })
        
        # Check for removed capabilities
        old_caps = set(old_info.get("capabilities", {}).keys())
        new_caps = set(new_version_info.get("capabilities", {}).keys())
        
        removed_caps = old_caps - new_caps
        if removed_caps:
            issues.append({
                "type": "capabilities_removed",
                "capabilities": list(removed_caps),
                "severity": "error",
                "message": (
                    f"Capabilities removed: {', '.join(removed_caps)}"
                ),
            })
        
        # Check for new capabilities (informational)
        added_caps = new_caps - old_caps
        if added_caps:
            warnings.append({
                "type": "capabilities_added",
                "capabilities": list(added_caps),
                "message": (
                    f"New capabilities: {', '.join(added_caps)}"
                ),
            })
        
        # Check for breaking changes in version
        old_version = old_info.get("version", "0.0.0")
        new_version = new_version_info.get("version", "0.0.0")
        
        if self._is_major_version_change(old_version, new_version):
            warnings.append({
                "type": "major_version_change",
                "old": old_version,
                "new": new_version,
                "message": "Major version change - review changelog",
            })
        
        return {
            "compatible": len([
                i for i in issues if i["severity"] == "error"
            ]) == 0,
            "issues": issues,
            "warnings": warnings,
        }
    
    async def health_check(
        self,
        client_key: str,
        client: Any,
        timeout: float = 10.0,
    ) -> Dict[str, Any]:
        """Perform health check on an MCP client.
        
        Args:
            client_key: Client identifier.
            client: MCP client instance.
            timeout: Health check timeout in seconds.
            
        Returns:
            Health check result:
            {
                "status": "healthy" | "unhealthy" | "unknown",
                "tools_count": int,
                "latency_ms": int,
                "last_check": str,
                "error": str (if unhealthy)
            }
        """
        start_time = datetime.now()
        
        try:
            # Try to list tools as health check
            tools = await asyncio.wait_for(
                client.list_tools(),
                timeout=timeout,
            )
            
            latency_ms = int(
                (datetime.now() - start_time).total_seconds() * 1000
            )
            
            result = {
                "status": "healthy",
                "tools_count": len(tools) if tools else 0,
                "latency_ms": latency_ms,
                "last_check": datetime.now().isoformat(),
                "error": None,
            }
            
            logger.debug(
                f"Health check passed for {client_key}: "
                f"{len(tools) if tools else 0} tools, "
                f"{latency_ms}ms latency"
            )
            
        except asyncio.TimeoutError:
            result = {
                "status": "unhealthy",
                "error": f"Health check timeout ({timeout}s)",
                "last_check": datetime.now().isoformat(),
            }
            logger.warning(
                f"Health check timeout for {client_key}"
            )
            
        except Exception as e:
            result = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat(),
            }
            logger.error(
                f"Health check failed for {client_key}: {e}"
            )
        
        # Store result
        self.health_check_results[client_key] = result
        
        # Update tracker file
        self._update_health_status(client_key, result)
        
        return result
    
    def start_health_checks(self, clients: Dict[str, Any]):
        """Start background health check task.
        
        Args:
            clients: Dictionary of client_key -> client instance.
        """
        self._clients = clients
        
        if self._health_check_task is None or self._health_check_task.done():
            self._health_check_task = asyncio.create_task(
                self._run_periodic_health_checks(),
                name="mcp_health_check_task",
            )
            logger.info(
                f"Started MCP health checks "
                f"(interval: {self.health_check_interval}s)"
            )
    
    def stop_health_checks(self) -> None:
        """Stop background health check task."""
        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            logger.info("Stopped MCP health checks")
    
    def list_clients(self) -> List[Dict[str, Any]]:
        """List all tracked clients with their version info.
        
        Returns:
            List of client information dictionaries.
        """
        data = self.load()
        
        clients = []
        for key, info in data["clients"].items():
            health = self.health_check_results.get(key, {})
            
            clients.append({
                "key": key,
                "version": info.get("version", "unknown"),
                "protocol_version": info.get(
                    "protocol_version", "unknown"
                ),
                "capabilities": info.get("capabilities", {}),
                "health_status": health.get(
                    "status", info.get("health_status", "unknown")
                ),
                "last_check": health.get(
                    "last_check", info.get("last_health_check")
                ),
                "latency_ms": health.get("latency_ms"),
                "tools_count": health.get("tools_count"),
                "last_updated": info.get("last_updated"),
            })
        
        return clients
    
    def get_client_info(
        self,
        client_key: str,
    ) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific client.
        
        Args:
            client_key: Client identifier.
            
        Returns:
            Client information dictionary, or None if not found.
        """
        data = self.load()
        
        if client_key not in data["clients"]:
            return None
        
        info = data["clients"][client_key]
        health = self.health_check_results.get(client_key, {})
        
        return {
            "key": client_key,
            "version": info.get("version", "unknown"),
            "protocol_version": info.get("protocol_version", "unknown"),
            "capabilities": info.get("capabilities", {}),
            "health_status": health.get(
                "status", info.get("health_status", "unknown")
            ),
            "health_history": info.get("health_history", []),
            "version_history": info.get("version_history", []),
            "last_updated": info.get("last_updated"),
            "config_hash": info.get("config_hash"),
        }
    
    def get_version_history(
        self,
        client_key: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get version history for a client.
        
        Args:
            client_key: Client identifier.
            limit: Maximum number of versions to return.
            
        Returns:
            List of version records.
        """
        data = self.load()
        
        if client_key not in data["clients"]:
            return []
        
        history = data["clients"][client_key].get("version_history", [])
        return history[-limit:]
    
    def rollback_version(
        self,
        client_key: str,
        target_version: str,
    ) -> Dict[str, Any]:
        """Rollback a client to a previous version.
        
        Note: This only updates the tracker record. Actual rollback
        requires reconfiguring the client.
        
        Args:
            client_key: Client identifier.
            target_version: Version to rollback to.
            
        Returns:
            Rollback result dictionary.
        """
        data = self.load()
        
        if client_key not in data["clients"]:
            return {
                "success": False,
                "error": f"Client '{client_key}' not found.",
            }
        
        history = data["clients"][client_key].get("version_history", [])
        
        # Find target version in history
        target_record = None
        for record in history:
            if record.get("version") == target_version:
                target_record = record
                break
        
        if not target_record:
            return {
                "success": False,
                "error": (
                    f"Version '{target_version}' not found in history."
                ),
            }
        
        # Update current version to target
        old_version = data["clients"][client_key].get("version")
        data["clients"][client_key]["version"] = target_version
        data["clients"][client_key]["last_updated"] = (
            datetime.now().isoformat()
        )
        data["clients"][client_key]["rollback_from"] = old_version
        
        self.save(data)
        
        logger.info(
            f"Rolled back {client_key} from {old_version} "
            f"to {target_version}"
        )
        
        return {
            "success": True,
            "client_key": client_key,
            "from_version": old_version,
            "to_version": target_version,
        }
    
    def _update_health_status(
        self,
        client_key: str,
        result: Dict[str, Any],
    ) -> None:
        """Update health status in tracker file.
        
        Args:
            client_key: Client identifier.
            result: Health check result.
        """
        data = self.load()
        
        if client_key in data["clients"]:
            data["clients"][client_key]["health_status"] = result[
                "status"
            ]
            data["clients"][client_key]["last_health_check"] = result[
                "last_check"
            ]
            data["clients"][client_key]["health_check_count"] = (
                data["clients"][client_key].get("health_check_count", 0)
                + 1
            )
            
            # Add to health history (keep last 20)
            health_history = data["clients"][client_key].get(
                "health_history", []
            )
            health_history.append({
                "timestamp": result["last_check"],
                "status": result["status"],
                "latency_ms": result.get("latency_ms"),
                "error": result.get("error"),
            })
            data["clients"][client_key]["health_history"] = (
                health_history[-20:]
            )
        
        self.save(data)
    
    async def _run_periodic_health_checks(self) -> None:
        """Run periodic health checks on all clients."""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                for client_key, client in self._clients.items():
                    try:
                        await self.health_check(client_key, client)
                    except Exception as e:
                        logger.error(
                            f"Health check failed for {client_key}: {e}"
                        )
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    f"Health check task error: {e}", exc_info=True
                )
                await asyncio.sleep(self.health_check_interval)
    
    def _append_to_history(
        self,
        old_info: Dict[str, Any],
        new_info: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Append version change to history.
        
        Args:
            old_info: Previous version information.
            new_info: New version information.
            
        Returns:
            Updated history list.
        """
        history = old_info.get("version_history", [])
        
        # Add new record
        history.append({
            "version": new_info.get("version", "unknown"),
            "protocol_version": new_info.get(
                "protocol_version", "unknown"
            ),
            "timestamp": datetime.now().isoformat(),
            "capabilities": new_info.get("capabilities", {}),
        })
        
        # Keep last 10 versions
        return history[-10:]
    
    @staticmethod
    def _hash_config(config: Dict[str, Any]) -> str:
        """Calculate SHA256 hash of configuration.
        
        Args:
            config: Configuration dictionary.
            
        Returns:
            SHA256 hash hex string.
        """
        config_str = json.dumps(
            config, sort_keys=True, ensure_ascii=False
        )
        return hashlib.sha256(
            config_str.encode("utf-8")
        ).hexdigest()
    
    @staticmethod
    def _is_major_version_change(
        old_version: str,
        new_version: str,
    ) -> bool:
        """Check if version change is a major version bump.
        
        Args:
            old_version: Old version string (e.g., "1.2.3").
            new_version: New version string.
            
        Returns:
            True if major version changed.
        """
        def parse_version(v: str) -> tuple:
            parts = v.split(".")
            try:
                return (
                    int(parts[0]) if len(parts) > 0 else 0,
                    int(parts[1]) if len(parts) > 1 else 0,
                    int(parts[2]) if len(parts) > 2 else 0,
                )
            except ValueError:
                return (0, 0, 0)
        
        old_major, _, _ = parse_version(old_version)
        new_major, _, _ = parse_version(new_version)
        
        return old_major != new_major


# Global instance for convenience
MCP_VERSION_TRACKER = MCPVersionTracker()
