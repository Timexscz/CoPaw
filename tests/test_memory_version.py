# -*- coding: utf-8 -*-
"""Unit tests for memory version_manager module."""
import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from copaw.agents.memory.version_manager import MemoryVersionManager


@pytest.fixture
def temp_memory_dir():
    """Create a temporary memory directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def version_manager(temp_memory_dir):
    """Create a MemoryVersionManager instance with temp directory."""
    return MemoryVersionManager(temp_memory_dir, max_versions=5)


@pytest.fixture
def sample_memory_file(temp_memory_dir):
    """Create a sample memory file for tests."""
    memory_file = temp_memory_dir / "MEMORY.md"
    memory_file.write_text(
        "# Memory\n\nThis is test content.",
        encoding="utf-8",
    )
    return memory_file


class TestMemoryVersionManager:
    """Test cases for MemoryVersionManager."""
    
    def test_init(self, temp_memory_dir):
        """Test MemoryVersionManager initialization."""
        manager = MemoryVersionManager(temp_memory_dir)
        
        assert manager.memory_dir == temp_memory_dir
        assert manager.version_dir == temp_memory_dir / ".versions"
        assert manager.max_versions == 10
    
    def test_init_creates_directories(self, temp_memory_dir):
        """Test that initialization creates required directories."""
        new_dir = temp_memory_dir / "new_memory"
        manager = MemoryVersionManager(new_dir)
        
        assert new_dir.exists()
        assert (new_dir / ".versions").exists()
    
    def test_save_version_from_file(
        self,
        version_manager,
        sample_memory_file,
    ):
        """Test saving version from existing file."""
        version_path = version_manager.save_version("MEMORY.md")
        
        assert Path(version_path).exists()
        assert "MEMORY.md" in version_path
        
        # Verify content includes metadata
        content = Path(version_path).read_text(encoding="utf-8")
        assert "version_timestamp:" in content
        assert "original_filename:" in content
        assert "This is test content." in content
    
    def test_save_version_with_content(
        self,
        version_manager,
    ):
        """Test saving version with provided content."""
        content = "# New Content\n\nNew test content."
        version_path = version_manager.save_version(
            "TEST.md",
            content=content,
        )
        
        assert Path(version_path).exists()
        
        # Verify content
        saved_content = Path(version_path).read_text(encoding="utf-8")
        assert "New test content." in saved_content
    
    def test_save_version_not_found(self, version_manager):
        """Test saving version when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            version_manager.save_version("NONEXISTENT.md")
    
    def test_list_versions_empty(self, version_manager):
        """Test listing versions when none exist."""
        versions = version_manager.list_versions("MEMORY.md")
        
        assert versions == []
    
    def test_list_versions(
        self,
        version_manager,
        sample_memory_file,
    ):
        """Test listing available versions."""
        # Save multiple versions
        version_manager.save_version(
            "MEMORY.md",
            message="Version 1",
        )
        
        # Modify and save again
        sample_memory_file.write_text(
            "# Memory\n\nUpdated content.",
            encoding="utf-8",
        )
        version_manager.save_version(
            "MEMORY.md",
            message="Version 2",
        )
        
        versions = version_manager.list_versions("MEMORY.md")
        
        assert len(versions) == 2
        assert versions[0]["filename"] == "MEMORY.md"
        assert "timestamp" in versions[0]
    
    def test_list_versions_limit(
        self,
        version_manager,
        sample_memory_file,
    ):
        """Test listing versions with limit."""
        # Save 10 versions
        for i in range(10):
            version_manager.save_version(
                "MEMORY.md",
                message=f"Version {i}",
            )
        
        versions = version_manager.list_versions(
            "MEMORY.md",
            limit=5,
        )
        
        assert len(versions) == 5
    
    def test_restore_version(
        self,
        version_manager,
        sample_memory_file,
    ):
        """Test restoring a version."""
        # Save version
        version_path = version_manager.save_version(
            "MEMORY.md",
            message="Original",
        )
        
        # Modify original
        sample_memory_file.write_text(
            "# Memory\n\nModified content.",
            encoding="utf-8",
        )
        
        # Restore
        restored_path = version_manager.restore_version(version_path)
        
        assert Path(restored_path).exists()
        
        # Verify content restored
        content = sample_memory_file.read_text(encoding="utf-8")
        assert "This is test content." in content
    
    def test_restore_version_not_found(
        self,
        version_manager,
    ):
        """Test restoring non-existent version."""
        with pytest.raises(FileNotFoundError):
            version_manager.restore_version("/nonexistent/path.md")
    
    def test_restore_with_backup(
        self,
        version_manager,
        sample_memory_file,
    ):
        """Test that restore creates backup."""
        # Save version
        version_path = version_manager.save_version("MEMORY.md")
        
        # Modify
        sample_memory_file.write_text(
            "# Memory\n\nModified.",
            encoding="utf-8",
        )
        
        # Restore (should create backup)
        version_manager.restore_version(version_path, backup=True)
        
        # Check backup was created
        versions = version_manager.list_versions("MEMORY.md")
        assert len(versions) >= 2
    
    def test_diff_versions(
        self,
        version_manager,
        sample_memory_file,
    ):
        """Test comparing two versions."""
        # Save first version
        v1_path = version_manager.save_version(
            "MEMORY.md",
            message="V1",
        )
        
        # Modify and save second version
        sample_memory_file.write_text(
            "# Memory\n\nChanged content.",
            encoding="utf-8",
        )
        v2_path = version_manager.save_version(
            "MEMORY.md",
            message="V2",
        )
        
        # Get diff
        diff = version_manager.diff_versions(v1_path, v2_path)
        
        assert isinstance(diff, str)
        assert "---" in diff
        assert "+++" in diff
    
    def test_diff_with_current(
        self,
        version_manager,
        sample_memory_file,
    ):
        """Test comparing version with current file."""
        # Save version
        version_path = version_manager.save_version("MEMORY.md")
        
        # Modify current
        sample_memory_file.write_text(
            "# Memory\n\nNew content.",
            encoding="utf-8",
        )
        
        # Get diff
        diff = version_manager.diff_with_current(version_path)
        
        assert isinstance(diff, str)
        assert len(diff) > 0
    
    def test_delete_version(
        self,
        version_manager,
        sample_memory_file,
    ):
        """Test deleting a version."""
        # Save version
        version_path = version_manager.save_version("MEMORY.md")
        
        # Delete
        result = version_manager.delete_version(version_path)
        
        assert result is True
        assert not Path(version_path).exists()
    
    def test_delete_nonexistent_version(
        self,
        version_manager,
    ):
        """Test deleting non-existent version."""
        result = version_manager.delete_version("/nonexistent/path")
        
        assert result is False
    
    def test_cleanup(
        self,
        version_manager,
        sample_memory_file,
    ):
        """Test cleaning up old versions."""
        # Save more than max_versions
        for i in range(10):
            version_manager.save_version(
                "MEMORY.md",
                message=f"V{i}",
            )
        
        # Cleanup
        result = version_manager.cleanup(dry_run=True)
        
        assert result["deleted_count"] > 0
        assert result["kept_count"] == version_manager.max_versions
        assert result["dry_run"] is True
    
    def test_cleanup_dry_run(
        self,
        version_manager,
        sample_memory_file,
    ):
        """Test cleanup dry run doesn't delete."""
        # Save versions
        for i in range(10):
            version_manager.save_version("MEMORY.md")
        
        # Count before
        before_count = len(
            list(version_manager.version_dir.iterdir())
        )
        
        # Cleanup dry run
        version_manager.cleanup(dry_run=True)
        
        # Count after (should be same)
        after_count = len(
            list(version_manager.version_dir.iterdir())
        )
        
        assert before_count == after_count
    
    def test_auto_cleanup_on_save(
        self,
        version_manager,
        sample_memory_file,
    ):
        """Test that save_version auto-cleans old versions."""
        # Save more than max_versions (5)
        for i in range(10):
            version_manager.save_version("MEMORY.md")
        
        # Should only keep max_versions
        versions = version_manager.list_versions("MEMORY.md")
        
        assert len(versions) <= version_manager.max_versions
    
    def test_parse_version_metadata(self, version_manager):
        """Test parsing metadata from version file."""
        content = (
            "---\n"
            "version_timestamp: 2025-03-12T10:00:00\n"
            "original_filename: MEMORY.md\n"
            "message: Test save\n"
            "content_length: 100\n"
            "---\n\n"
            "Actual content here."
        )
        
        metadata = version_manager._parse_version_metadata(content)
        
        assert metadata["version_timestamp"] == "2025-03-12T10:00:00"
        assert metadata["original_filename"] == "MEMORY.md"
        assert metadata["message"] == "Test save"
        assert metadata["content_length"] == "100"
    
    def test_extract_content_from_version(
        self,
        version_manager,
    ):
        """Test extracting content from version file."""
        content = (
            "---\n"
            "version_timestamp: 2025-03-12T10:00:00\n"
            "---\n\n"
            "Actual content here."
        )
        
        extracted = version_manager._extract_content_from_version(
            content
        )
        
        assert extracted == "Actual content here."
    
    def test_extract_content_no_metadata(
        self,
        version_manager,
    ):
        """Test extracting content when no metadata present."""
        content = "Just content, no metadata."
        
        extracted = version_manager._extract_content_from_version(
            content
        )
        
        assert extracted == content
