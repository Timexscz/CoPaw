# -*- coding: utf-8 -*-
"""Unit tests for MCP version_tracker module."""
import asyncio
import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from copaw.app.mcp.version_tracker import MCPVersionTracker


@pytest.fixture
def temp_working_dir():
    """Create a temporary working directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def version_tracker(temp_working_dir):
    """Create a MCPVersionTracker instance with temp directory."""
    return MCPVersionTracker(
        temp_working_dir,
        health_check_interval=60,
    )


class TestMCPVersionTracker:
    """Test cases for MCPVersionTracker."""
    
    def test_init(self, temp_working_dir):
        """Test MCPVersionTracker initialization."""
        tracker = MCPVersionTracker(temp_working_dir)
        
        assert tracker.working_dir == temp_working_dir
        assert tracker.tracker_file == temp_working_dir / "mcp_versions.json"
        assert tracker.health_check_interval == 300
    
    def test_load_empty(self, version_tracker):
        """Test loading when no tracker file exists."""
        data = version_tracker.load()
        
        assert data["version"] == 1
        assert data["clients"] == {}
        assert "created_at" in data
    
    def test_save_and_load(self, version_tracker):
        """Test saving and loading tracker data."""
        data = {
            "version": 1,
            "clients": {
                "test_client": {
                    "version": "1.0.0",
                },
            },
        }
        
        version_tracker.save(data)
        
        # Load and verify
        loaded = version_tracker.load()
        
        assert loaded["clients"]["test_client"]["version"] == "1.0.0"
    
    def test_record_version(self, version_tracker):
        """Test recording version information."""
        version_info = {
            "version": "1.0.0",
            "protocol_version": "2024-11-05",
            "capabilities": {"tools": True, "resources": False},
        }
        
        version_tracker.record_version(
            "test_client",
            version_info,
        )
        
        # Verify saved
        data = version_tracker.load()
        
        assert "test_client" in data["clients"]
        assert data["clients"]["test_client"]["version"] == "1.0.0"
        assert (
            data["clients"]["test_client"]["protocol_version"]
            == "2024-11-05"
        )
    
    def test_record_version_with_config(self, version_tracker):
        """Test recording version with config hash."""
        version_info = {"version": "1.0.0"}
        config = {"url": "http://localhost:8080", "timeout": 30}
        
        version_tracker.record_version(
            "test_client",
            version_info,
            config=config,
        )
        
        data = version_tracker.load()
        
        assert "config_hash" in data["clients"]["test_client"]
        assert len(data["clients"]["test_client"]["config_hash"]) == 64
    
    def test_check_compatibility_no_previous(
        self,
        version_tracker,
    ):
        """Test compatibility check with no previous version."""
        new_version = {
            "version": "1.0.0",
            "protocol_version": "2024-11-05",
        }
        
        result = version_tracker.check_compatibility(
            "new_client",
            new_version,
        )
        
        assert result["compatible"] is True
        assert len(result["issues"]) == 0
    
    def test_check_compatibility_protocol_mismatch(
        self,
        version_tracker,
    ):
        """Test compatibility with protocol version mismatch."""
        # Record old version
        version_tracker.record_version(
            "test_client",
            {
                "version": "1.0.0",
                "protocol_version": "2024-01-01",
            },
        )
        
        # Check new version with different protocol
        new_version = {
            "version": "2.0.0",
            "protocol_version": "2024-11-05",
        }
        
        result = version_tracker.check_compatibility(
            "test_client",
            new_version,
        )
        
        assert result["compatible"] is True  # Warning, not error
        assert len(result["issues"]) == 1
        assert result["issues"][0]["type"] == "protocol_mismatch"
    
    def test_check_compatibility_removed_capabilities(
        self,
        version_tracker,
    ):
        """Test compatibility with removed capabilities."""
        # Record old version with capabilities
        version_tracker.record_version(
            "test_client",
            {
                "version": "1.0.0",
                "capabilities": {"tools": True, "resources": True},
            },
        )
        
        # Check new version with fewer capabilities
        new_version = {
            "version": "1.1.0",
            "capabilities": {"tools": True},  # resources removed
        }
        
        result = version_tracker.check_compatibility(
            "test_client",
            new_version,
        )
        
        assert result["compatible"] is False  # Error level
        assert any(
            i["type"] == "capabilities_removed"
            for i in result["issues"]
        )
    
    def test_check_compatibility_added_capabilities(
        self,
        version_tracker,
    ):
        """Test compatibility with new capabilities."""
        # Record old version
        version_tracker.record_version(
            "test_client",
            {
                "version": "1.0.0",
                "capabilities": {"tools": True},
            },
        )
        
        # Check new version with more capabilities
        new_version = {
            "version": "1.1.0",
            "capabilities": {"tools": True, "resources": True},
        }
        
        result = version_tracker.check_compatibility(
            "test_client",
            new_version,
        )
        
        assert result["compatible"] is True
        assert len(result["warnings"]) > 0
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(
        self,
        version_tracker,
    ):
        """Test health check with healthy client."""
        # Mock client
        mock_client = AsyncMock()
        mock_client.list_tools = AsyncMock(
            return_value=[{"name": "tool1"}, {"name": "tool2"}]
        )
        
        result = await version_tracker.health_check(
            "test_client",
            mock_client,
        )
        
        assert result["status"] == "healthy"
        assert result["tools_count"] == 2
        assert "latency_ms" in result
        assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_health_check_timeout(
        self,
        version_tracker,
    ):
        """Test health check with timeout."""
        # Mock client that times out
        mock_client = AsyncMock()
        mock_client.list_tools = AsyncMock(
            side_effect=asyncio.TimeoutError()
        )
        
        result = await version_tracker.health_check(
            "test_client",
            mock_client,
            timeout=0.1,
        )
        
        assert result["status"] == "unhealthy"
        assert "timeout" in result["error"]
    
    @pytest.mark.asyncio
    async def test_health_check_error(
        self,
        version_tracker,
    ):
        """Test health check with error."""
        # Mock client that raises error
        mock_client = AsyncMock()
        mock_client.list_tools = AsyncMock(
            side_effect=Exception("Connection failed")
        )
        
        result = await version_tracker.health_check(
            "test_client",
            mock_client,
        )
        
        assert result["status"] == "unhealthy"
        assert "Connection failed" in result["error"]
    
    def test_list_clients_empty(self, version_tracker):
        """Test listing clients when none tracked."""
        clients = version_tracker.list_clients()
        
        assert clients == []
    
    def test_list_clients(self, version_tracker):
        """Test listing tracked clients."""
        # Record some clients
        version_tracker.record_version(
            "client1",
            {"version": "1.0.0", "protocol_version": "2024-11-05"},
        )
        version_tracker.record_version(
            "client2",
            {"version": "2.0.0", "protocol_version": "2024-11-05"},
        )
        
        clients = version_tracker.list_clients()
        
        assert len(clients) == 2
        assert clients[0]["key"] == "client1"
        assert clients[1]["key"] == "client2"
    
    def test_get_client_info(self, version_tracker):
        """Test getting detailed client info."""
        version_tracker.record_version(
            "test_client",
            {
                "version": "1.0.0",
                "protocol_version": "2024-11-05",
                "capabilities": {"tools": True},
            },
        )
        
        info = version_tracker.get_client_info("test_client")
        
        assert info is not None
        assert info["key"] == "test_client"
        assert info["version"] == "1.0.0"
        assert "version_history" in info
    
    def test_get_client_info_not_found(
        self,
        version_tracker,
    ):
        """Test getting non-existent client info."""
        info = version_tracker.get_client_info("nonexistent")
        
        assert info is None
    
    def test_get_version_history(self, version_tracker):
        """Test getting version history."""
        # Record multiple versions
        for i in range(5):
            version_tracker.record_version(
                "test_client",
                {"version": f"{i + 1}.0.0"},
            )
        
        history = version_tracker.get_version_history(
            "test_client",
            limit=3,
        )
        
        assert len(history) == 3
    
    def test_rollback_version(self, version_tracker):
        """Test rolling back to previous version."""
        # Record initial version
        version_tracker.record_version(
            "test_client",
            {"version": "1.0.0"},
        )
        
        # Record second version
        version_tracker.record_version(
            "test_client",
            {"version": "2.0.0"},
        )
        
        # Rollback
        result = version_tracker.rollback_version(
            "test_client",
            "1.0.0",
        )
        
        assert result["success"] is True
        assert result["from_version"] == "2.0.0"
        assert result["to_version"] == "1.0.0"
    
    def test_rollback_version_not_found(
        self,
        version_tracker,
    ):
        """Test rolling back to non-existent version."""
        version_tracker.record_version(
            "test_client",
            {"version": "1.0.0"},
        )
        
        result = version_tracker.rollback_version(
            "test_client",
            "9.9.9",
        )
        
        assert result["success"] is False
        assert "not found" in result["error"]
    
    def test_rollback_client_not_found(
        self,
        version_tracker,
    ):
        """Test rolling back non-existent client."""
        result = version_tracker.rollback_version(
            "nonexistent",
            "1.0.0",
        )
        
        assert result["success"] is False
    
    def test_hash_config(self, version_tracker):
        """Test config hashing."""
        config1 = {"url": "http://localhost", "timeout": 30}
        config2 = {"timeout": 30, "url": "http://localhost"}  # Same, different order
        
        hash1 = version_tracker._hash_config(config1)
        hash2 = version_tracker._hash_config(config2)
        
        assert hash1 == hash2  # Should be same due to sort_keys
        assert len(hash1) == 64  # SHA256 hex length
    
    def test_is_major_version_change(self, version_tracker):
        """Test major version change detection."""
        assert (
            version_tracker._is_major_version_change(
                "1.0.0", "2.0.0"
            )
            is True
        )
        assert (
            version_tracker._is_major_version_change(
                "1.0.0", "1.1.0"
            )
            is False
        )
        assert (
            version_tracker._is_major_version_change(
                "1.9.9", "2.0.0"
            )
            is True
        )
    
    def test_version_history_appended(
        self,
        version_tracker,
    ):
        """Test that version history is appended."""
        # Record multiple versions
        version_tracker.record_version(
            "test_client",
            {"version": "1.0.0"},
        )
        version_tracker.record_version(
            "test_client",
            {"version": "2.0.0"},
        )
        
        data = version_tracker.load()
        history = data["clients"]["test_client"]["version_history"]
        
        assert len(history) == 2
        assert history[0]["version"] == "1.0.0"
        assert history[1]["version"] == "2.0.0"
    
    def test_version_history_limited(
        self,
        version_tracker,
    ):
        """Test that version history is limited to 10 entries."""
        # Record 15 versions
        for i in range(15):
            version_tracker.record_version(
                "test_client",
                {"version": f"{i + 1}.0.0"},
            )
        
        data = version_tracker.load()
        history = data["clients"]["test_client"]["version_history"]
        
        assert len(history) == 10
