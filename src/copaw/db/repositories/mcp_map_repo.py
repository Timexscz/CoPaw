# -*- coding: utf-8 -*-
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
"""MCP client category mapping repository."""

import json
from typing import Optional, Dict, List

from ..database import db


class MCPCategoryMapRepository:
    """Repository for MCP client-category mapping operations."""
    
    @staticmethod
    async def set_category(
        client_key: str,
        category_id: str,
        is_manual: bool = False,
        confidence: int = 0,
        matched_keywords: Optional[List[str]] = None,
    ) -> None:
        """
        Set category for an MCP client.
        
        Args:
            client_key: Key of the MCP client
            category_id: ID of the category
            is_manual: Whether this is a manual assignment
            confidence: AI confidence score (0-100)
            matched_keywords: List of matched keywords
        """
        async with db.acquire() as conn:
            await conn.execute("""
                INSERT INTO mcp_category_map 
                (client_key, category_id, is_manual, ai_confidence, matched_keywords)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (client_key) DO UPDATE SET
                    category_id = EXCLUDED.category_id,
                    is_manual = EXCLUDED.is_manual,
                    ai_confidence = EXCLUDED.ai_confidence,
                    matched_keywords = EXCLUDED.matched_keywords,
                    updated_at = CURRENT_TIMESTAMP
            """,
                client_key,
                category_id,
                is_manual,
                confidence,
                json.dumps(matched_keywords) if matched_keywords else None,
            )
        
        # Clear cache
        await db.redis.delete(f"mcp_category:{client_key}")
    
    @staticmethod
    async def get_category(client_key: str) -> Optional[str]:
        """
        Get category for an MCP client.
        
        Args:
            client_key: Key of the MCP client
            
        Returns:
            Category ID or None
        """
        # Try cache first
        cache_key = f"mcp_category:{client_key}"
        cached = await db.redis.get(cache_key)
        
        if cached:
            return cached
        
        # Query database
        async with db.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT category_id FROM mcp_category_map 
                WHERE client_key = $1
            """, client_key)
        
        if row is None:
            return None
        
        # Cache for 5 minutes
        await db.redis.setex(cache_key, 300, row['category_id'])
        
        return row['category_id']
    
    @staticmethod
    async def batch_get_categories(client_keys: List[str]) -> Dict[str, str]:
        """
        Get categories for multiple MCP clients.
        
        Args:
            client_keys: List of client keys
            
        Returns:
            Dictionary mapping client keys to category IDs
        """
        # Try cache first
        cache_keys = [f"mcp_category:{key}" for key in client_keys]
        cached_values = await db.redis.mget(cache_keys)
        
        result: Dict[str, str] = {}
        missing: List[str] = []
        
        for key, value in zip(client_keys, cached_values):
            if value:
                result[key] = value
            else:
                missing.append(key)
        
        # Query database for missing
        if missing:
            async with db.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT client_key, category_id FROM mcp_category_map 
                    WHERE client_key = ANY($1)
                """, missing)
                
                for row in rows:
                    result[row['client_key']] = row['category_id']
                    # Cache for 5 minutes
                    await db.redis.setex(
                        f"mcp_category:{row['client_key']}",
                        300,
                        row['category_id']
                    )
        
        return result
    
    @staticmethod
    async def clear_category(client_key: str) -> None:
        """
        Clear category assignment for an MCP client.
        
        Args:
            client_key: Key of the MCP client
        """
        async with db.acquire() as conn:
            await conn.execute("""
                DELETE FROM mcp_category_map WHERE client_key = $1
            """, client_key)
        
        # Clear cache
        await db.redis.delete(f"mcp_category:{client_key}")
