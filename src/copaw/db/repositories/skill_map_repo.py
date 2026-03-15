"""Skill category mapping repository."""

import json
from typing import Optional, Dict, List

from ..database import db


class SkillCategoryMapRepository:
    """Repository for skill-category mapping operations."""
    
    @staticmethod
    async def set_category(
        skill_name: str,
        category_id: str,
        is_manual: bool = False,
        confidence: int = 0,
        matched_keywords: Optional[List[str]] = None,
    ) -> None:
        """
        Set category for a skill.
        
        Args:
            skill_name: Name of the skill
            category_id: ID of the category
            is_manual: Whether this is a manual assignment
            confidence: AI confidence score (0-100)
            matched_keywords: List of matched keywords
        """
        async with db.acquire() as conn:
            await conn.execute("""
                INSERT INTO skill_category_map 
                (skill_name, category_id, is_manual, ai_confidence, matched_keywords)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (skill_name) DO UPDATE SET
                    category_id = EXCLUDED.category_id,
                    is_manual = EXCLUDED.is_manual,
                    ai_confidence = EXCLUDED.ai_confidence,
                    matched_keywords = EXCLUDED.matched_keywords,
                    updated_at = CURRENT_TIMESTAMP
            """,
                skill_name,
                category_id,
                is_manual,
                confidence,
                json.dumps(matched_keywords) if matched_keywords else None,
            )
        
        # Clear cache
        await db.redis.delete(f"skill_category:{skill_name}")
    
    @staticmethod
    async def get_category(skill_name: str) -> Optional[str]:
        """
        Get category for a skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Category ID or None
        """
        # Try cache first
        cache_key = f"skill_category:{skill_name}"
        cached = await db.redis.get(cache_key)
        
        if cached:
            return cached
        
        # Query database
        async with db.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT category_id FROM skill_category_map 
                WHERE skill_name = $1
            """, skill_name)
        
        if row is None:
            return None
        
        # Cache for 5 minutes
        await db.redis.setex(cache_key, 300, row['category_id'])
        
        return row['category_id']
    
    @staticmethod
    async def batch_get_categories(skill_names: List[str]) -> Dict[str, str]:
        """
        Get categories for multiple skills.
        
        Args:
            skill_names: List of skill names
            
        Returns:
            Dictionary mapping skill names to category IDs
        """
        # Try cache first
        cache_keys = [f"skill_category:{name}" for name in skill_names]
        cached_values = await db.redis.mget(cache_keys)
        
        result: Dict[str, str] = {}
        missing: List[str] = []
        
        for name, value in zip(skill_names, cached_values):
            if value:
                result[name] = value
            else:
                missing.append(name)
        
        # Query database for missing
        if missing:
            async with db.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT skill_name, category_id FROM skill_category_map 
                    WHERE skill_name = ANY($1)
                """, missing)
                
                for row in rows:
                    result[row['skill_name']] = row['category_id']
                    # Cache for 5 minutes
                    await db.redis.setex(
                        f"skill_category:{row['skill_name']}",
                        300,
                        row['category_id']
                    )
        
        return result
    
    @staticmethod
    async def clear_category(skill_name: str) -> None:
        """
        Clear category assignment for a skill.
        
        Args:
            skill_name: Name of the skill
        """
        async with db.acquire() as conn:
            await conn.execute("""
                DELETE FROM skill_category_map WHERE skill_name = $1
            """, skill_name)
        
        # Clear cache
        await db.redis.delete(f"skill_category:{skill_name}")
