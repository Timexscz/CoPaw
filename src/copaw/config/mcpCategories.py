# -*- coding: utf-8 -*-
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
"""
MCP category configuration for Python backend.
Mirrors the frontend categorization logic.
"""

from typing import Dict, List, Any, Callable


def _match_database(client: Dict[str, Any]) -> bool:
    """Match database-related MCP clients."""
    name = (client.get('name', '') + ' ' + client.get('description', '')).lower()
    return any(kw in name for kw in ['postgres', 'mysql', 'sqlite', 'mongo', 'redis', 'database', 'sql'])


def _match_filesystem(client: Dict[str, Any]) -> bool:
    """Match filesystem-related MCP clients."""
    name = (client.get('name', '') + ' ' + client.get('description', '')).lower()
    return any(kw in name for kw in ['file', 'filesystem', 'storage', 'disk'])


def _match_api(client: Dict[str, Any]) -> bool:
    """Match API integration MCP clients."""
    name = (client.get('name', '') + ' ' + client.get('description', '')).lower()
    return any(kw in name for kw in ['api', 'rest', 'graphql', 'webhook'])


def _match_ai(client: Dict[str, Any]) -> bool:
    """Match AI service MCP clients."""
    name = (client.get('name', '') + ' ' + client.get('description', '')).lower()
    return any(kw in name for kw in ['llm', 'model', 'ai', 'embedding', 'chat', 'openai', 'anthropic'])


def _match_productivity(client: Dict[str, Any]) -> bool:
    """Match productivity MCP clients."""
    name = (client.get('name', '') + ' ' + client.get('description', '')).lower()
    return any(kw in name for kw in ['calendar', 'todo', 'task', 'note', 'notion', 'slack'])


def _match_local(client: Dict[str, Any]) -> bool:
    """Match local (stdio) MCP clients."""
    return client.get('transport') == 'stdio' or (not client.get('transport') and client.get('command'))


def _match_remote_http(client: Dict[str, Any]) -> bool:
    """Match remote HTTP MCP clients."""
    return client.get('transport') in ['streamable_http', 'http']


def _match_remote_sse(client: Dict[str, Any]) -> bool:
    """Match remote SSE MCP clients."""
    return client.get('transport') == 'sse'


# Default MCP categories
MCP_CATEGORIES: List[Dict[str, Any]] = [
    {
        'id': 'database',
        'name': '数据库',
        'icon': '🗄️',
        'color': '#722ed1',
        'matcher': _match_database,
        'priority': 10,
    },
    {
        'id': 'filesystem',
        'name': '文件系统',
        'icon': '📁',
        'color': '#faad14',
        'matcher': _match_filesystem,
        'priority': 9,
    },
    {
        'id': 'api',
        'name': 'API 集成',
        'icon': '🔌',
        'color': '#13c2c2',
        'matcher': _match_api,
        'priority': 8,
    },
    {
        'id': 'ai',
        'name': 'AI 服务',
        'icon': '🤖',
        'color': '#eb2f96',
        'matcher': _match_ai,
        'priority': 7,
    },
    {
        'id': 'productivity',
        'name': '效率工具',
        'icon': '📊',
        'color': '#2f54eb',
        'matcher': _match_productivity,
        'priority': 6,
    },
    {
        'id': 'local',
        'name': '本地服务',
        'icon': '💻',
        'color': '#1890ff',
        'matcher': _match_local,
        'priority': 5,
    },
    {
        'id': 'remote_http',
        'name': '远程 HTTP',
        'icon': '🌐',
        'color': '#52c41a',
        'matcher': _match_remote_http,
        'priority': 4,
    },
    {
        'id': 'remote_sse',
        'name': '远程 SSE',
        'icon': '📡',
        'color': '#fa8c16',
        'matcher': _match_remote_sse,
        'priority': 3,
    },
]

DEFAULT_CATEGORY = {
    'id': 'other',
    'name': '其他',
    'icon': '📦',
    'color': '#d9d9d9',
    'matcher': lambda x: True,  # Always matches
    'priority': 0,
}


def categorizeMCP(client: Dict[str, Any]) -> str:
    """
    Categorize an MCP client based on its configuration.
    
    Args:
        client: Dict with 'name', 'description', 'transport', 'command', 'url' keys
        
    Returns:
        Category ID
    """
    # Sort categories by priority (highest first)
    sorted_categories = sorted(MCP_CATEGORIES, key=lambda x: x['priority'], reverse=True)
    
    # Find the first matching category
    for category in sorted_categories:
        matcher = category.get('matcher')
        if matcher and matcher(client):
            return category['id']
    
    # Return default category if no match
    return DEFAULT_CATEGORY['id']


def get_category_by_id(category_id: str) -> Dict[str, Any]:
    """Get category information by ID."""
    for category in MCP_CATEGORIES:
        if category['id'] == category_id:
            return category
    return DEFAULT_CATEGORY


def get_all_categories() -> List[Dict[str, Any]]:
    """Get all categories including default."""
    return MCP_CATEGORIES + [DEFAULT_CATEGORY]
