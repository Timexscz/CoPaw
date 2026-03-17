# -*- coding: utf-8 -*-
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
"""Category service for business logic."""

from typing import List, Tuple, Optional

from ..db.repositories import CategoryRepository, CategoryModel, SkillCategoryMapRepository
from ..config.skillCategories import categorizeSkill as frontend_categorize_skill
from ..config.mcpCategories import categorizeMCP as frontend_categorize_mcp


class CategoryService:
    """Service for category-related business logic."""
    
    @staticmethod
    async def get_skill_categories(enabled_only: bool = True) -> List[CategoryModel]:
        """
        Get skill categories.
        
        Args:
            enabled_only: If True, only return enabled categories
            
        Returns:
            List of CategoryModel objects
        """
        return await CategoryRepository.get_categories('skill', enabled_only)
    
    @staticmethod
    async def get_mcp_categories(enabled_only: bool = True) -> List[CategoryModel]:
        """
        Get MCP categories.
        
        Args:
            enabled_only: If True, only return enabled categories
            
        Returns:
            List of CategoryModel objects
        """
        return await CategoryRepository.get_categories('mcp', enabled_only)
    
    @staticmethod
    async def categorize_skill(
        name: str,
        description: str = '',
        content: str = '',
        force_reanalyze: bool = False,
    ) -> Tuple[str, int, List[str]]:
        """
        Categorize a skill using AI/intelligent matching.
        
        Args:
            name: Skill name
            description: Skill description
            content: Full skill content (SKILL.md)
            force_reanalyze: If True, re-categorize even if manual assignment exists
            
        Returns:
            Tuple of (category_id, confidence, matched_keywords)
        """
        # Check for manual assignment first
        if not force_reanalyze:
            manual_category = await SkillCategoryMapRepository.get_category(name)
            if manual_category:
                return (manual_category, 100, [])
        
        # Use frontend categorization logic (keyword matching)
        category_id = frontend_categorize_skill({
            'name': name,
            'description': description,
            'content': content,
        })
        
        # Calculate confidence and matched keywords
        confidence, matched = await CategoryService._calculate_confidence(
            name, description, content, category_id
        )
        
        # Save to database
        await SkillCategoryMapRepository.set_category(
            skill_name=name,
            category_id=category_id,
            is_manual=False,
            confidence=confidence,
            matched_keywords=matched,
        )
        
        return (category_id, confidence, matched)
    
    @staticmethod
    async def categorize_mcp_client(
        name: str,
        description: str = '',
        transport: str = '',
        command: str = '',
        url: str = '',
        force_reanalyze: bool = False,
    ) -> Tuple[str, int, List[str]]:
        """
        Categorize an MCP client.
        
        Args:
            name: Client name
            description: Client description
            transport: Transport type (stdio/streamable_http/sse)
            command: Command for stdio transport
            url: URL for HTTP/SSE transport
            force_reanalyze: If True, re-categorize even if manual assignment exists
            
        Returns:
            Tuple of (category_id, confidence, matched_keywords)
        """
        # Check for manual assignment first
        # (Would use MCPCategoryMapRepository similar to skills)
        
        # Use frontend categorization logic
        category_id = frontend_categorize_mcp({
            'name': name,
            'description': description,
            'transport': transport,
            'command': command,
            'url': url,
        })
        
        # For MCP, confidence is based on transport match or keyword match
        if transport in ['stdio', 'streamable_http', 'sse']:
            confidence = 90  # High confidence for transport-based
            matched = [transport]
        else:
            confidence = 70
            matched = []
        
        return (category_id, confidence, matched)
    
    @staticmethod
    async def set_manual_category(
        skill_name: str,
        category_id: str,
    ) -> None:
        """
        Manually set category for a skill.
        
        Args:
            skill_name: Name of the skill
            category_id: ID of the category
        """
        await SkillCategoryMapRepository.set_category(
            skill_name=skill_name,
            category_id=category_id,
            is_manual=True,
        )
    
    @staticmethod
    async def _calculate_confidence(
        name: str,
        description: str,
        content: str,
        category_id: str,
    ) -> Tuple[int, List[str]]:
        """
        Calculate categorization confidence.
        
        Args:
            name: Skill name
            description: Skill description
            content: Full skill content
            category_id: Target category ID
            
        Returns:
            Tuple of (confidence_score, matched_keywords)
        """
        category = await CategoryRepository.get_category(category_id)
        if not category:
            return (0, [])
        
        search_text = f"{name} {description} {content}".lower()
        matched = [kw for kw in category.keywords if kw.lower() in search_text]
        
        # Simple confidence calculation: 15 points per matched keyword, max 100
        confidence = min(100, len(matched) * 15)
        
        return (confidence, matched)
