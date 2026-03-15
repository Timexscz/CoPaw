# -*- coding: utf-8 -*-
"""Memory version manager for CoPaw.

This module provides version control functionality for memory files,
enabling users to save, restore, and compare different versions of
memory content.

Key Features:
    - Save versions before modifications
    - Restore previous versions
    - Compare differences between versions
    - Automatic version cleanup (keep recent N versions)
    - Version metadata tracking
"""
import difflib
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

# Lazy import to avoid circular dependency
def _get_memory_dir():
    from ...constant import MEMORY_DIR
    return MEMORY_DIR

def _get_working_dir():
    from ...constant import WORKING_DIR
    return WORKING_DIR

logger = logging.getLogger(__name__)


class MemoryVersionManager:
    """Memory file version manager.
    
    Manages versions of memory files with support for:
    - Manual version saving
    - Automatic versioning on writes
    - Version restoration
    - Diff comparison
    
    Attributes:
        memory_dir: Path to memory directory
        version_dir: Path to .versions subdirectory
        max_versions: Maximum versions to keep per file
    """
    
    def __init__(
        self,
        memory_dir: Optional[Path] = None,
        max_versions: int = 10,
    ):
        """Initialize MemoryVersionManager.
        
        Args:
            memory_dir: Memory directory path. Defaults to MEMORY_DIR.
            max_versions: Maximum versions to retain per file.
        """
        self.memory_dir = memory_dir or _get_memory_dir()
        self.version_dir = self.memory_dir / ".versions"
        self.max_versions = max_versions
        
        # Ensure directories exist
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.version_dir.mkdir(parents=True, exist_ok=True)
    
    def save_version(
        self,
        filename: str,
        content: Optional[str] = None,
        message: str = "",
    ) -> str:
        """Save a version of a memory file.
        
        Args:
            filename: Name of the memory file (e.g., "MEMORY.md").
            content: Optional content to save. If None, reads from file.
            message: Optional version message.
            
        Returns:
            Path to saved version file as string.
            
        Raises:
            FileNotFoundError: If file doesn't exist and content not provided.
        """
        # Normalize filename
        if not filename.endswith(".md"):
            filename += ".md"
        
        # Get content
        if content is None:
            file_path = self.memory_dir / filename
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Memory file not found: {filename}"
                )
            content = file_path.read_text(encoding="utf-8")
        
        # Generate version filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_filename = f"{filename}.{timestamp}"
        version_path = self.version_dir / version_filename
        
        # Save version with metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "filename": filename,
            "message": message,
            "content_length": len(content),
        }
        
        # Write version file with metadata header
        version_content = (
            f"---\n"
            f"version_timestamp: {metadata['timestamp']}\n"
            f"original_filename: {metadata['filename']}\n"
            f"message: {metadata['message']}\n"
            f"content_length: {metadata['content_length']}\n"
            f"---\n\n"
            f"{content}"
        )
        
        version_path.write_text(
            version_content,
            encoding="utf-8",
        )
        
        logger.info(
            f"Saved version of {filename} -> {version_path}"
        )
        
        # Cleanup old versions
        self._cleanup_old_versions(filename)
        
        return str(version_path)
    
    def list_versions(
        self,
        filename: str,
        limit: int = 20,
    ) -> list[dict]:
        """List available versions for a file.
        
        Args:
            filename: Name of the memory file.
            limit: Maximum number of versions to return.
            
        Returns:
            List of version metadata dictionaries:
            [{
                "path": str,
                "filename": str,
                "timestamp": str,
                "message": str,
                "content_length": int,
                "size": int
            }]
        """
        # Normalize filename
        if not filename.endswith(".md"):
            filename += ".md"
        
        # Find all versions
        pattern = f"{filename}.*"
        versions = []
        
        for version_file in sorted(
            self.version_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:limit]:
            try:
                content = version_file.read_text(encoding="utf-8")
                
                # Parse metadata from front matter
                metadata = self._parse_version_metadata(content)
                
                versions.append({
                    "path": str(version_file),
                    "filename": filename,
                    "timestamp": metadata.get(
                        "timestamp",
                        datetime.fromtimestamp(
                            version_file.stat().st_mtime
                        ).isoformat(),
                    ),
                    "message": metadata.get("message", ""),
                    "content_length": metadata.get("content_length", 0),
                    "size": version_file.stat().st_size,
                })
            except Exception as e:
                logger.debug(
                    f"Failed to parse version {version_file}: {e}"
                )
        
        return versions
    
    def restore_version(
        self,
        version_path: str,
        backup: bool = True,
    ) -> str:
        """Restore a memory file from a version.
        
        Args:
            version_path: Path to version file.
            backup: If True, backup current file before restore.
            
        Returns:
            Path to restored file as string.
            
        Raises:
            FileNotFoundError: If version file doesn't exist.
        """
        version_file = Path(version_path)
        
        if not version_file.exists():
            raise FileNotFoundError(
                f"Version file not found: {version_path}"
            )
        
        # Read version content (skip metadata)
        content = version_file.read_text(encoding="utf-8")
        content = self._extract_content_from_version(content)
        
        # Extract original filename
        metadata = self._parse_version_metadata(content)
        original_filename = metadata.get("filename", "")
        
        if not original_filename:
            # Try to extract from version filename
            parts = version_file.name.split(".")
            if len(parts) >= 3:
                original_filename = ".".join(parts[:-2])
            else:
                raise ValueError(
                    "Cannot determine original filename from version"
                )
        
        target_file = self.memory_dir / original_filename
        
        # Backup current file if exists
        if backup and target_file.exists():
            backup_path = self.save_version(
                original_filename,
                message=f"Backup before restore from {version_file.name}",
            )
            logger.info(f"Created backup: {backup_path}")
        
        # Restore content
        target_file.write_text(content, encoding="utf-8")
        
        logger.info(
            f"Restored {original_filename} from {version_path}"
        )
        
        return str(target_file)
    
    def diff_versions(
        self,
        version_path1: str,
        version_path2: str,
        context: int = 3,
    ) -> str:
        """Compare two versions and return unified diff.
        
        Args:
            version_path1: Path to first version file.
            version_path2: Path to second version file.
            context: Number of context lines in diff.
            
        Returns:
            Unified diff string.
        """
        # Read both versions
        content1 = self._read_version_content(version_path1)
        content2 = self._read_version_content(version_path2)
        
        # Generate diff
        diff = difflib.unified_diff(
            content1.splitlines(keepends=True),
            content2.splitlines(keepends=True),
            fromfile=version_path1,
            tofile=version_path2,
            n=context,
        )
        
        return "".join(diff)
    
    def diff_with_current(
        self,
        version_path: str,
        context: int = 3,
    ) -> str:
        """Compare a version with current file content.
        
        Args:
            version_path: Path to version file.
            context: Number of context lines in diff.
            
        Returns:
            Unified diff string.
        """
        # Read version content
        version_content = self._read_version_content(version_path)
        
        # Extract filename from version
        version_text = Path(version_path).read_text(encoding="utf-8")
        metadata = self._parse_version_metadata(version_text)
        filename = metadata.get("filename", "")
        
        if not filename:
            parts = Path(version_path).name.split(".")
            if len(parts) >= 3:
                filename = ".".join(parts[:-2])
        
        # Read current content
        current_file = self.memory_dir / filename
        if current_file.exists():
            current_content = current_file.read_text(encoding="utf-8")
        else:
            current_content = ""
        
        # Generate diff
        diff = difflib.unified_diff(
            version_content.splitlines(keepends=True),
            current_content.splitlines(keepends=True),
            fromfile=version_path,
            tofile=str(current_file),
            n=context,
        )
        
        return "".join(diff)
    
    def delete_version(self, version_path: str) -> bool:
        """Delete a specific version.
        
        Args:
            version_path: Path to version file.
            
        Returns:
            True if deleted, False if failed.
        """
        version_file = Path(version_path)
        
        if not version_file.exists():
            return False
        
        try:
            version_file.unlink()
            logger.info(f"Deleted version: {version_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete version: {e}")
            return False
    
    def cleanup(self, dry_run: bool = False) -> dict:
        """Clean up old versions across all files.
        
        Args:
            dry_run: If True, only show what would be deleted.
            
        Returns:
            Cleanup summary dictionary.
        """
        # Group versions by filename
        versions_by_file: dict[str, list[Path]] = {}
        
        for version_file in self.version_dir.iterdir():
            if not version_file.is_file():
                continue
            
            # Extract filename from version filename
            name = version_file.name
            parts = name.split(".")
            if len(parts) >= 3:
                filename = ".".join(parts[:-2])
            else:
                continue
            
            if filename not in versions_by_file:
                versions_by_file[filename] = []
            versions_by_file[filename].append(version_file)
        
        # Cleanup each file's versions
        deleted = []
        kept = []
        
        for filename, versions in versions_by_file.items():
            # Sort by timestamp (newest first)
            sorted_versions = sorted(
                versions,
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            
            # Keep only max_versions
            to_keep = sorted_versions[: self.max_versions]
            to_delete = sorted_versions[self.max_versions :]
            
            kept.extend([str(v) for v in to_keep])
            
            for version in to_delete:
                if dry_run:
                    deleted.append(str(version) + " (dry run)")
                else:
                    try:
                        version.unlink()
                        deleted.append(str(version))
                    except Exception as e:
                        logger.error(
                            f"Failed to delete {version}: {e}"
                        )
        
        return {
            "deleted": deleted,
            "kept": kept,
            "deleted_count": len(deleted),
            "kept_count": len(kept),
            "dry_run": dry_run,
        }
    
    def _cleanup_old_versions(self, filename: str):
        """Remove old versions, keeping only max_versions.
        
        Args:
            filename: Name of the file to cleanup.
        """
        # Normalize filename
        if not filename.endswith(".md"):
            filename += ".md"
        
        pattern = f"{filename}.*"
        versions = sorted(
            self.version_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        
        # Delete excess versions
        for old_version in versions[self.max_versions :]:
            try:
                old_version.unlink()
                logger.debug(f"Cleaned up old version: {old_version}")
            except Exception as e:
                logger.warning(
                    f"Failed to cleanup {old_version}: {e}"
                )
    
    def _parse_version_metadata(
        self,
        content: str,
    ) -> dict[str, str]:
        """Parse metadata from version file front matter.
        
        Args:
            content: Version file content.
            
        Returns:
            Metadata dictionary.
        """
        metadata = {}
        
        if not content.startswith("---"):
            return metadata
        
        # Find end of front matter
        lines = content.split("\n")
        end_index = -1
        
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                end_index = i
                break
        
        if end_index == -1:
            return metadata
        
        # Parse YAML-like metadata
        for line in lines[1:end_index]:
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()
        
        return metadata
    
    def _extract_content_from_version(
        self,
        content: str,
    ) -> str:
        """Extract actual content from version file (skip metadata).
        
        Args:
            content: Version file content.
            
        Returns:
            Content without metadata header.
        """
        if not content.startswith("---"):
            return content
        
        # Find end of front matter
        lines = content.split("\n")
        end_index = -1
        
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                end_index = i
                break
        
        if end_index == -1:
            return content
        
        # Return content after front matter
        return "\n".join(lines[end_index + 1 :]).strip()
    
    def _read_version_content(
        self,
        version_path: str,
    ) -> str:
        """Read content from version file (skip metadata).
        
        Args:
            version_path: Path to version file.
            
        Returns:
            Content without metadata header.
        """
        version_file = Path(version_path)
        
        if not version_file.exists():
            raise FileNotFoundError(
                f"Version file not found: {version_path}"
            )
        
        content = version_file.read_text(encoding="utf-8")
        return self._extract_content_from_version(content)


# Global instance for convenience
MEMORY_VERSION_MANAGER = MemoryVersionManager()
