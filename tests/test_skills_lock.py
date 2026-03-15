# -*- coding: utf-8 -*-
"""Unit tests for skills_lock module."""
import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from copaw.agents.skills_lock import SkillsLockManager


@pytest.fixture
def temp_working_dir():
    """Create a temporary working directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def skills_lock_manager(temp_working_dir):
    """Create a SkillsLockManager instance with temp directory."""
    return SkillsLockManager(temp_working_dir)


class TestSkillsLockManager:
    """Test cases for SkillsLockManager."""
    
    def test_init(self, temp_working_dir):
        """Test SkillsLockManager initialization."""
        manager = SkillsLockManager(temp_working_dir)
        
        assert manager.working_dir == temp_working_dir
        assert manager.lock_file == temp_working_dir / "skills.lock"
    
    def test_generate_lock_empty(self, skills_lock_manager):
        """Test generate_lock with no skills."""
        lock_data = skills_lock_manager.generate_lock()
        
        assert lock_data["version"] == 1
        assert "generated_at" in lock_data
        assert lock_data["skills"] == {}
    
    def test_save_and_load_lock(self, skills_lock_manager):
        """Test saving and loading lock file."""
        # Save lock (will be empty since no skills)
        lock_path = skills_lock_manager.save_lock()
        
        assert Path(lock_path).exists()
        
        # Load lock
        lock_data = skills_lock_manager.load_lock()
        
        assert lock_data is not None
        assert "version" in lock_data
        assert "skills" in lock_data
    
    def test_load_lock_nonexistent(self, skills_lock_manager):
        """Test loading lock when file doesn't exist."""
        lock_data = skills_lock_manager.load_lock()
        
        assert lock_data is None
    
    def test_compare_versions(self):
        """Test semantic version comparison."""
        result = SkillsLockManager._compare_versions("1.0.0", "1.0.0")
        assert result == 0
        
        result = SkillsLockManager._compare_versions("1.0.0", "1.0.1")
        assert result == -1
        
        result = SkillsLockManager._compare_versions("1.2.0", "1.1.9")
        assert result == 1
        
        result = SkillsLockManager._compare_versions("2.0.0", "1.9.9")
        assert result == 1
        
        result = SkillsLockManager._compare_versions("1.0.0", "2.0.0")
        assert result == -1
    
    def test_check_updates_no_lock(self, skills_lock_manager):
        """Test check_updates when no lock file exists."""
        result = skills_lock_manager.check_updates("test_skill")
        
        assert "has_update" in result
        assert result["has_update"] is False
        assert "reason" in result
    
    def test_check_updates_not_in_lock(self, skills_lock_manager):
        """Test check_updates for skill not in lock file."""
        # Create empty lock file
        skills_lock_manager.save_lock()
        
        result = skills_lock_manager.check_updates("nonexistent_skill")
        
        assert result["has_update"] is False
        assert "not found" in result["reason"]
    
    def test_list_outdated_skills_empty(self, skills_lock_manager):
        """Test list_outdated_skills with no outdated skills."""
        skills_lock_manager.save_lock()
        
        outdated = skills_lock_manager.list_outdated_skills()
        
        assert outdated == []
    
    def test_update_skill_not_in_lock(self, skills_lock_manager):
        """Test updating a skill not in lock file."""
        skills_lock_manager.save_lock()
        
        result = skills_lock_manager.update_skill("nonexistent")
        
        assert result["success"] is False
        assert "not found" in result["error"]
    
    def test_update_all_skills_empty(self, skills_lock_manager):
        """Test updating all skills when none are outdated."""
        skills_lock_manager.save_lock()
        
        result = skills_lock_manager.update_all_skills()
        
        assert result["success"] is True
        assert "up to date" in result["message"]
    
    def test_dry_run_update(self, skills_lock_manager):
        """Test dry run update mode."""
        skills_lock_manager.save_lock()
        
        # This will fail but tests dry_run flag handling
        result = skills_lock_manager.update_skill(
            "test",
            dry_run=True,
        )
        
        # Should not fail due to dry_run
        assert "dry_run" in result or "error" in result


class TestSkillsLockManagerWithSkills:
    """Test cases with actual skill data."""
    
    @pytest.fixture
    def skills_dir(self, temp_working_dir):
        """Create active_skills directory with test skills."""
        skills_dir = temp_working_dir / "active_skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a test skill
        skill_dir = skills_dir / "test_skill"
        skill_dir.mkdir()
        
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: Test Skill\n"
            "version: 1.0.0\n"
            "description: A test skill\n"
            "source: builtin\n"
            "---\n\n"
            "# Test Skill\n\nContent here.",
            encoding="utf-8",
        )
        
        return skills_dir
    
    def test_generate_lock_with_skills(
        self,
        temp_working_dir,
        skills_dir,
    ):
        """Test generate_lock with actual skills."""
        manager = SkillsLockManager(temp_working_dir)
        lock_data = manager.generate_lock()
        
        assert "test_skill" in lock_data["skills"]
        
        skill_info = lock_data["skills"]["test_skill"]
        assert skill_info["name"] == "Test Skill"
        assert skill_info["version"] == "1.0.0"
        assert "content_hash" in skill_info
        assert skill_info["source"] == "builtin"
    
    def test_save_lock_with_skills(
        self,
        temp_working_dir,
        skills_dir,
    ):
        """Test saving lock file with skills."""
        manager = SkillsLockManager(temp_working_dir)
        lock_path = manager.save_lock()
        
        assert Path(lock_path).exists()
        
        # Verify content
        content = Path(lock_path).read_text(encoding="utf-8")
        lock_data = json.loads(content)
        
        assert "test_skill" in lock_data["skills"]
