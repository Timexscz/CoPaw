# -*- coding: utf-8 -*-
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
"""Skill parser for Markdown and Front Matter."""

from pathlib import Path
from typing import Tuple, Dict, Any, Optional

import frontmatter
import markdown


class SkillParser:
    """Parser for SKILL.md files."""
    
    @staticmethod
    def parse_skill_md(file_path: Path) -> Tuple[Dict[str, Any], str]:
        """
        Parse a SKILL.md file.
        
        Args:
            file_path: Path to SKILL.md file
            
        Returns:
            Tuple of (metadata_dict, html_content)
        """
        post = frontmatter.load(file_path)
        
        metadata = {
            'name': post.get('name', ''),
            'description': post.get('description', ''),
            'metadata': post.get('metadata', {}),
            'category': post.get('category'),  # Optional backend category
        }
        
        # Convert Markdown to HTML
        html = markdown.markdown(
            post.content,
            extensions=[
                'fenced_code',  # ```code``` support
                'tables',       # Table support
                'toc',          # Table of contents
                'nl2br',        # Newline to <br>
            ],
            output_format='html5'
        )
        
        return metadata, html
    
    @staticmethod
    def parse_skill_content(content: str) -> Tuple[Dict[str, Any], str]:
        """
        Parse SKILL.md content from string.
        
        Args:
            content: Raw SKILL.md content
            
        Returns:
            Tuple of (metadata_dict, html_content)
        """
        post = frontmatter.loads(content)
        
        metadata = {
            'name': post.get('name', ''),
            'description': post.get('description', ''),
            'metadata': post.get('metadata', {}),
            'category': post.get('category'),
        }
        
        html = markdown.markdown(
            post.content,
            extensions=[
                'fenced_code',
                'tables',
                'toc',
                'nl2br',
            ],
            output_format='html5'
        )
        
        return metadata, html
    
    @staticmethod
    def extract_category_from_content(content: str) -> Optional[str]:
        """
        Extract category from SKILL.md Front Matter.
        
        Args:
            content: Raw SKILL.md content
            
        Returns:
            Category ID or None
        """
        try:
            post = frontmatter.loads(content)
            return post.get('category')
        except Exception:
            return None
