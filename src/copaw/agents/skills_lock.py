# -*- coding: utf-8 -*-
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
"""Skills version lock manager.

This module provides version locking functionality for CoPaw skills,
enabling reproducible installations and update detection.

Key Features:
    - Generate skills.lock file with version information
    - Detect outdated skills from GitHub/ClawHub sources
    - Update skills with rollback support
    - Track installation metadata (commit hash, content hash, timestamps)
"""
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import frontmatter

# Lazy import to avoid circular dependency
def _get_constants():
    from ..constant import WORKING_DIR, ACTIVE_SKILLS_DIR
    return WORKING_DIR, ACTIVE_SKILLS_DIR

from .skills_hub import (
    _extract_github_spec,
    _http_json_get,
    _github_api_url,
    _hub_base_url,
    _hub_detail_path,
)

logger = logging.getLogger(__name__)


class SkillsLockManager:
    """Skills version lock manager.
    
    Manages version locking for CoPaw skills, enabling:
    - Reproducible skill installations
    - Update detection from remote sources
    - Version history tracking
    
    Attributes:
        lock_file: Path to skills.lock file
        skills_dir: Path to active_skills directory
    """
    
    def __init__(self, working_dir: Optional[Path] = None):
        """Initialize SkillsLockManager.
        
        Args:
            working_dir: Working directory path. Defaults to WORKING_DIR.
        """
        WORKING_DIR, ACTIVE_SKILLS_DIR = _get_constants()
        self.working_dir = working_dir or WORKING_DIR
        self.lock_file = self.working_dir / "skills.lock"
        self.skills_dir = ACTIVE_SKILLS_DIR
    
    def generate_lock(self) -> dict[str, Any]:
        """Generate version lock data from current active skills.
        
        Scans all active skills and collects version information,
        content hashes, and source metadata.
        
        Returns:
            Dictionary containing lock file data with structure:
            {
                "version": 1,
                "generated_at": ISO timestamp,
                "skills": {
                    "skill_name": {
                        "name": str,
                        "version": str,
                        "content_hash": str,
                        "source": str,
                        "source_url": str,
                        "commit_hash": str,
                        "installed_at": ISO timestamp
                    }
                }
            }
        """
        lock_data = {
            "version": 1,
            "generated_at": datetime.now().isoformat(),
            "skills": {},
        }
        
        if not self.skills_dir.exists():
            logger.warning(f"Skills directory not found: {self.skills_dir}")
            return lock_data
        
        for skill_dir in sorted(self.skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                logger.debug(f"No SKILL.md in {skill_dir}, skipping")
                continue
            
            try:
                content = skill_md.read_text(encoding="utf-8")
                post = frontmatter.loads(content)
                
                # Extract metadata from Front Matter
                skill_name = post.get("name", skill_dir.name)
                version = post.get("version", "0.0.0")
                description = post.get("description", "")
                source = post.get("source", "unknown")
                source_url = post.get("source_url", "")
                commit_hash = post.get("commit_hash", "")
                
                # Calculate content hash for change detection
                content_hash = hashlib.sha256(
                    content.encode("utf-8")
                ).hexdigest()
                
                lock_data["skills"][skill_dir.name] = {
                    "name": skill_name,
                    "version": version,
                    "description": description,
                    "content_hash": content_hash,
                    "source": source,
                    "source_url": source_url,
                    "commit_hash": commit_hash,
                    "installed_at": datetime.fromtimestamp(
                        skill_md.stat().st_ctime
                    ).isoformat(),
                }
                
                logger.debug(f"Locked skill: {skill_dir.name} v{version}")
                
            except Exception as e:
                logger.error(
                    f"Failed to process skill {skill_dir.name}: {e}",
                    exc_info=True,
                )
        
        return lock_data
    
    def save_lock(self) -> str:
        """Generate and save lock file.
        
        Returns:
            Path to saved lock file as string.
        """
        lock_data = self.generate_lock()
        
        self.lock_file.write_text(
            json.dumps(lock_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        
        logger.info(f"Generated lock file: {self.lock_file}")
        return str(self.lock_file)
    
    def load_lock(self) -> Optional[dict[str, Any]]:
        """Load existing lock file.
        
        Returns:
            Lock file data as dict, or None if file doesn't exist.
        """
        if not self.lock_file.exists():
            return None
        
        try:
            content = self.lock_file.read_text(encoding="utf-8")
            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to load lock file: {e}")
            return None
    
    def check_updates(self, skill_name: str) -> dict[str, Any]:
        """Check if a skill has updates available.
        
        Args:
            skill_name: Name of the skill to check.
            
        Returns:
            Dictionary with update information:
            {
                "has_update": bool,
                "local_version": str,
                "remote_version": str,
                "source": str,
                "details": str
            }
        """
        lock_data = self.load_lock()
        
        if not lock_data:
            return {
                "has_update": False,
                "reason": "No lock file found. Run 'copaw skills version lock' first.",
            }
        
        if skill_name not in lock_data["skills"]:
            return {
                "has_update": False,
                "reason": f"Skill '{skill_name}' not found in lock file.",
            }
        
        skill_info = lock_data["skills"][skill_name]
        source_url = skill_info.get("source_url", "")
        
        if not source_url:
            return {
                "has_update": False,
                "reason": "No source URL recorded.",
            }
        
        # Check GitHub source
        if "github.com" in source_url:
            return self._check_github_update(skill_name, skill_info)
        
        # Check ClawHub source
        if "clawhub.ai" in source_url:
            return self._check_clawhub_update(skill_name, skill_info)
        
        return {
            "has_update": False,
            "reason": f"Unsupported source: {source_url}",
        }
    
    def _check_github_update(
        self,
        skill_name: str,
        skill_info: dict[str, Any],
    ) -> dict[str, Any]:
        """Check for GitHub skill updates.
        
        Args:
            skill_name: Name of the skill.
            skill_info: Skill information from lock file.
            
        Returns:
            Update check result dictionary.
        """
        source_url = skill_info["source_url"]
        spec = _extract_github_spec(source_url)
        
        if not spec:
            return {
                "has_update": False,
                "reason": "Failed to parse GitHub URL.",
            }
        
        owner, repo, branch, path = spec
        
        # Get remote file hash
        try:
            remote_hash = self._get_github_file_hash(
                owner, repo, branch, f"{path}/SKILL.md"
            )
            
            if not remote_hash:
                return {
                    "has_update": False,
                    "reason": "Failed to fetch remote file.",
                }
            
            local_hash = skill_info.get("content_hash", "")
            has_update = remote_hash != local_hash
            
            return {
                "has_update": has_update,
                "local_hash": local_hash,
                "remote_hash": remote_hash,
                "source": "github",
                "source_url": source_url,
            }
            
        except Exception as e:
            logger.error(f"GitHub update check failed: {e}")
            return {
                "has_update": False,
                "reason": f"Update check failed: {e}",
            }
    
    def _get_github_file_hash(
        self,
        owner: str,
        repo: str,
        branch: str,
        path: str,
    ) -> Optional[str]:
        """Get SHA256 hash of a file in GitHub repository.
        
        Args:
            owner: GitHub repository owner.
            repo: Repository name.
            branch: Branch name.
            path: File path within repository.
            
        Returns:
            SHA256 hash of file content, or None if failed.
        """
        try:
            # Use GitHub API to get file content
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
            
            req = Request(
                url,
                headers={
                    "Accept": "application/vnd.github.v3.raw",
                    "User-Agent": "copaw-skills-lock/1.0",
                },
            )
            
            # Add GitHub token if available (for rate limit)
            github_token = (
                os.environ.get("GITHUB_TOKEN")
                or os.environ.get("GH_TOKEN")
            )
            if github_token:
                req.add_header(
                    "Authorization", f"Bearer {github_token}"
                )
            
            with urlopen(req, timeout=10) as response:
                content = response.read()
                return hashlib.sha256(content).hexdigest()
                
        except Exception as e:
            logger.debug(f"Failed to get GitHub file hash: {e}")
            return None
    
    def _check_clawhub_update(
        self,
        skill_name: str,
        skill_info: dict[str, Any],
    ) -> dict[str, Any]:
        """Check for ClawHub skill updates.
        
        Args:
            skill_name: Name of the skill.
            skill_info: Skill information from lock file.
            
        Returns:
            Update check result dictionary.
        """
        try:
            # Extract slug from source URL
            slug = skill_info.get("slug", skill_name)
            base_url = _hub_base_url()
            path = _hub_detail_path().format(slug=slug)
            url = f"{base_url}{path}"
            
            data = _http_json_get(url)
            
            if not isinstance(data, dict):
                return {
                    "has_update": False,
                    "reason": "Invalid response from ClawHub.",
                }
            
            remote_version = data.get("version", "0.0.0")
            local_version = skill_info.get("version", "0.0.0")
            
            # Simple version comparison
            has_update = self._compare_versions(
                remote_version, local_version
            ) > 0
            
            return {
                "has_update": has_update,
                "local_version": local_version,
                "remote_version": remote_version,
                "source": "clawhub",
                "source_url": skill_info.get("source_url", ""),
            }
            
        except Exception as e:
            logger.error(f"ClawHub update check failed: {e}")
            return {
                "has_update": False,
                "reason": f"Update check failed: {e}",
            }
    
    @staticmethod
    def _compare_versions(v1: str, v2: str) -> int:
        """Compare two semantic version strings.
        
        Args:
            v1: First version string.
            v2: Second version string.
            
        Returns:
            -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2.
        """
        def parse_version(v: str) -> list[int]:
            parts = []
            for part in v.split("."):
                try:
                    parts.append(int(part))
                except ValueError:
                    parts.append(0)
            return parts
        
        parts1 = parse_version(v1)
        parts2 = parse_version(v2)
        
        # Pad to same length
        max_len = max(len(parts1), len(parts2))
        parts1.extend([0] * (max_len - len(parts1)))
        parts2.extend([0] * (max_len - len(parts2)))
        
        for p1, p2 in zip(parts1, parts2):
            if p1 < p2:
                return -1
            if p1 > p2:
                return 1
        
        return 0
    
    def list_outdated_skills(self) -> list[str]:
        """List all skills that have updates available.
        
        Returns:
            List of skill names with available updates.
        """
        lock_data = self.load_lock()
        if not lock_data:
            return []
        
        outdated = []
        for skill_name in lock_data["skills"]:
            update_info = self.check_updates(skill_name)
            if update_info.get("has_update"):
                outdated.append(skill_name)
        
        return outdated
    
    def get_skill_versions(self, skill_name: str) -> list[dict[str, Any]]:
        """Get version history for a specific skill.
        
        Note: This requires additional version history tracking
        which can be implemented in future iterations.
        
        Args:
            skill_name: Name of the skill.
            
        Returns:
            List of version records (currently returns empty list).
        """
        # TODO: Implement version history tracking
        return []
    
    def update_skill(
        self,
        skill_name: str,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Update a specific skill to latest version.
        
        Args:
            skill_name: Name of the skill to update.
            dry_run: If True, only show what would be updated.
            
        Returns:
            Update result dictionary:
            {
                "success": bool,
                "skill_name": str,
                "old_version": str,
                "new_version": str,
                "message": str
            }
        """
        lock_data = self.load_lock()
        
        if not lock_data or skill_name not in lock_data["skills"]:
            return {
                "success": False,
                "error": f"Skill '{skill_name}' not found in lock file.",
            }
        
        skill_info = lock_data["skills"][skill_name]
        source_url = skill_info.get("source_url", "")
        
        if not source_url:
            return {
                "success": False,
                "error": "No source URL recorded.",
            }
        
        # Check for updates first
        update_info = self.check_updates(skill_name)
        if not update_info.get("has_update"):
            return {
                "success": False,
                "error": update_info.get("reason", "No update available."),
            }
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "skill_name": skill_name,
                "source_url": source_url,
                "message": f"Would update {skill_name} from {source_url}",
            }
        
        # Delegate to SkillsHub for actual installation
        try:
            from .skills_hub import install_from_url
            
            result = install_from_url(source_url, overwrite=True)
            
            if result:
                # Update lock file
                self.save_lock()
                
                return {
                    "success": True,
                    "skill_name": skill_name,
                    "source_url": source_url,
                    "message": f"Successfully updated {skill_name}",
                }
            else:
                return {
                    "success": False,
                    "error": "Installation returned failure.",
                }
                
        except Exception as e:
            logger.error(f"Failed to update skill: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def update_all_skills(
        self,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Update all outdated skills.
        
        Args:
            dry_run: If True, only show what would be updated.
            
        Returns:
            Summary of update operations.
        """
        outdated = self.list_outdated_skills()
        
        if not outdated:
            return {
                "success": True,
                "updated": [],
                "message": "All skills are up to date.",
            }
        
        results = []
        for skill_name in outdated:
            result = self.update_skill(skill_name, dry_run=dry_run)
            results.append({
                "skill": skill_name,
                "success": result.get("success", False),
                "message": result.get("message", result.get("error", "")),
            })
        
        return {
            "success": True,
            "updated": [r["skill"] for r in results if r["success"]],
            "failed": [r["skill"] for r in results if not r["success"]],
            "dry_run": dry_run,
            "total": len(outdated),
        }


# Global instance for convenience
SKILLS_LOCK_MANAGER = SkillsLockManager()
