"""Category repository for database operations."""

import json
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, ConfigDict

from ..database import db


class CategoryModel(BaseModel):
    """Category data model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    icon: str
    color: str
    keywords: List[str]
    priority: int
    is_custom: bool = False
    is_enabled: bool = True
    category_type: str  # 'skill' | 'mcp'
    matcher_type: Optional[str] = None  # 'keyword' | 'transport'
    matcher_config: Optional[Dict[str, Any]] = None


class CategoryRepository:
    """Repository for category database operations."""
    
    @staticmethod
    async def get_categories(category_type: str, enabled_only: bool = False) -> List[CategoryModel]:
        """
        Get categories by type.
        
        Args:
            category_type: Type of categories ('skill' or 'mcp')
            enabled_only: If True, only return enabled categories
            
        Returns:
            List of CategoryModel objects
        """
        # Try cache first (if Redis is available)
        cache_key = f"categories:{category_type}:{'enabled' if enabled_only else 'all'}"
        try:
            cached = await db.redis.get(cache_key)
            if cached:
                return [CategoryModel(**item) for item in json.loads(cached)]
        except (RuntimeError, Exception):
            # Redis not available, skip cache
            pass
        
        # Query database
        async with db.acquire() as conn:
            if enabled_only:
                rows = await conn.fetch("""
                    SELECT * FROM categories 
                    WHERE category_type = $1 AND is_enabled = TRUE 
                    ORDER BY priority DESC
                """, category_type)
            else:
                rows = await conn.fetch("""
                    SELECT * FROM categories 
                    WHERE category_type = $1 
                    ORDER BY priority DESC
                """, category_type)
            
            categories = [
                CategoryModel(
                    id=row['id'],
                    name=row['name'],
                    icon=row['icon'],
                    color=row['color'],
                    keywords=row['keywords'] if isinstance(row['keywords'], list) else json.loads(row['keywords']) if row['keywords'] else [],
                    priority=row['priority'],
                    is_custom=row['is_custom'],
                    is_enabled=row['is_enabled'],
                    category_type=row['category_type'],
                    matcher_type=row['matcher_type'],
                    matcher_config=row['matcher_config'] if isinstance(row['matcher_config'], dict) else (json.loads(row['matcher_config']) if row['matcher_config'] else None),
                )
                for row in rows
            ]

        # Cache for 5 minutes (if Redis is available)
        try:
            await db.redis.setex(
                cache_key,
                300,
                json.dumps([cat.model_dump() for cat in categories])
            )
        except (RuntimeError, Exception):
            # Redis not available, skip caching
            pass

        return categories
    
    @staticmethod
    async def get_category(category_id: str) -> Optional[CategoryModel]:
        """Get a single category by ID."""
        async with db.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM categories WHERE id = $1
            """, category_id)
            
            if row is None:
                return None
            
            return CategoryModel(
                id=row['id'],
                name=row['name'],
                icon=row['icon'],
                color=row['color'],
                keywords=row['keywords'],
                priority=row['priority'],
                is_custom=row['is_custom'],
                is_enabled=row['is_enabled'],
                category_type=row['category_type'],
                matcher_type=row['matcher_type'],
                matcher_config=row['matcher_config'],
            )
    
    @staticmethod
    async def create_category(category: CategoryModel) -> CategoryModel:
        """Create or update a category."""
        async with db.acquire() as conn:
            await conn.execute("""
                INSERT INTO categories 
                (id, name, icon, color, keywords, priority, is_custom, is_enabled, 
                 category_type, matcher_type, matcher_config)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    icon = EXCLUDED.icon,
                    color = EXCLUDED.color,
                    keywords = EXCLUDED.keywords,
                    priority = EXCLUDED.priority,
                    is_custom = EXCLUDED.is_custom,
                    matcher_type = EXCLUDED.matcher_type,
                    matcher_config = EXCLUDED.matcher_config,
                    updated_at = CURRENT_TIMESTAMP
            """,
                category.id,
                category.name,
                category.icon,
                category.color,
                json.dumps(category.keywords),
                category.priority,
                category.is_custom,
                category.is_enabled,
                category.category_type,
                category.matcher_type,
                json.dumps(category.matcher_config) if category.matcher_config else None,
            )
        
        # Clear cache
        await db.redis.delete(f"categories:{category.category_type}:*")
        
        return category
    
    @staticmethod
    async def update_category_priority(category_ids: List[str], category_type: str) -> None:
        """
        Update category priorities (for reordering).
        
        Args:
            category_ids: List of category IDs in new order
            category_type: Type of categories
        """
        async with db.acquire() as conn:
            async with conn.transaction():
                for index, cat_id in enumerate(category_ids):
                    await conn.execute("""
                        UPDATE categories 
                        SET priority = $1 
                        WHERE id = $2 AND category_type = $3
                    """, len(category_ids) - index, cat_id, category_type)
        
        # Clear cache
        await db.redis.delete(f"categories:{category_type}:*")
    
    @staticmethod
    async def delete_category(category_id: str) -> bool:
        """
        Delete a category (only custom categories).
        
        Args:
            category_id: ID of category to delete
            
        Returns:
            True if deleted, False if not found or not custom
        """
        async with db.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT is_custom, category_type FROM categories WHERE id = $1
            """, category_id)
            
            if row is None or not row['is_custom']:
                return False
            
            await conn.execute("DELETE FROM categories WHERE id = $1", category_id)
            
            # Reset related skills to 'other'
            category_type = row['category_type']
            if category_type == 'skill':
                await conn.execute("""
                    UPDATE skill_category_map 
                    SET category_id = 'other' 
                    WHERE category_id = $1
                """, category_id)
            else:
                await conn.execute("""
                    UPDATE mcp_category_map 
                    SET category_id = 'other' 
                    WHERE category_id = $1
                """, category_id)
        
        # Clear cache
        await db.redis.delete(f"categories:{row['category_type']}:*")
        
        return True
    
    @staticmethod
    async def toggle_category(category_id: str) -> Optional[bool]:
        """
        Toggle category enabled status.
        
        Args:
            category_id: ID of category
            
        Returns:
            New enabled status, or None if not found
        """
        async with db.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT is_enabled, category_type FROM categories WHERE id = $1
            """, category_id)
            
            if row is None:
                return None
            
            new_status = not row['is_enabled']
            await conn.execute("""
                UPDATE categories SET is_enabled = $1 WHERE id = $2
            """, new_status, category_id)
        
        # Clear cache
        await db.redis.delete(f"categories:{row['category_type']}:*")
        
        return new_status
