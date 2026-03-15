"""
Skill category configuration for Python backend.
Mirrors the frontend categorization logic.
"""

from typing import Dict, List, Any


# Default skill categories with keywords
SKILL_CATEGORIES: List[Dict[str, Any]] = [
    {
        'id': 'document',
        'name': '文档处理',
        'icon': '📄',
        'color': '#1890ff',
        'keywords': ['docx', 'word', 'document', 'pdf', 'pptx', 'xlsx', 'excel', '文档'],
        'priority': 10,
    },
    {
        'id': 'communication',
        'name': '通讯工具',
        'icon': '📧',
        'color': '#52c41a',
        'keywords': ['email', 'imap', 'smtp', 'mail', 'dingtalk', 'discord', 'telegram', 'slack', '邮件', '通讯'],
        'priority': 9,
    },
    {
        'id': 'automation',
        'name': '自动化',
        'icon': '⚙️',
        'color': '#fa8c16',
        'keywords': ['cron', 'schedule', '定时', 'automation', 'automated', '定时任务', '计划任务', '自动化'],
        'priority': 9,
    },
    {
        'id': 'browser',
        'name': '浏览器',
        'icon': '🌐',
        'color': '#722ed1',
        'keywords': ['browser', 'web', 'http', 'url', 'navigate', 'click', 'snapshot', '浏览器', '网页'],
        'priority': 9,
    },
    {
        'id': 'media',
        'name': '媒体处理',
        'icon': '🎵',
        'color': '#eb2f96',
        'keywords': ['audio', 'video', 'music', 'himalaya', 'podcast', 'image', 'photo', 'media', '音频', '视频', '音乐', '媒体'],
        'priority': 8,
    },
    {
        'id': 'news',
        'name': '新闻资讯',
        'icon': '📰',
        'color': '#faad14',
        'keywords': ['news', 'article', 'rss', 'feed', 'headline', '新闻', '资讯', '文章', '订阅'],
        'priority': 7,
    },
    {
        'id': 'lifestyle',
        'name': '生活服务',
        'icon': '🌟',
        'color': '#13c2c2',
        'keywords': ['weather', 'forecast', 'calendar', 'event', 'reminder', 'shopping', 'food', 'restaurant', 'travel', '天气', '日历', '提醒', '生活'],
        'priority': 6,
    },
    {
        'id': 'productivity',
        'name': '效率工具',
        'icon': '📊',
        'color': '#2f54eb',
        'keywords': ['note', 'todo', 'task', 'project', 'manage', 'search', 'find', 'organize', '笔记', '待办', '任务', '管理', '搜索', '效率'],
        'priority': 6,
    },
    {
        'id': 'development',
        'name': '开发工具',
        'icon': '💻',
        'color': '#52c41a',
        'keywords': ['code', 'git', 'github', 'api', 'database', 'sql', 'debug', 'test', 'deploy', '代码', '开发', '数据库', 'API', '测试'],
        'priority': 5,
    },
    {
        'id': 'ai',
        'name': 'AI 工具',
        'icon': '🤖',
        'color': '#722ed1',
        'keywords': ['llm', 'model', 'ai', 'chatbot', 'generate', 'embedding', 'vector', 'ml', '人工智能', '模型', '生成', '机器学习'],
        'priority': 5,
    },
]

DEFAULT_CATEGORY = {
    'id': 'other',
    'name': '其他',
    'icon': '📦',
    'color': '#d9d9d9',
    'keywords': [],
    'priority': 0,
}


def categorizeSkill(params: Dict[str, str]) -> str:
    """
    Categorize a skill based on its content.
    
    Args:
        params: Dict with 'name', 'description', 'content' keys
        
    Returns:
        Category ID
    """
    name = params.get('name', '')
    description = params.get('description', '')
    content = params.get('content', '')
    
    # Combine all text for analysis
    search_text = f"{name} {description} {content}".lower()
    
    # Sort categories by priority (highest first)
    sorted_categories = sorted(SKILL_CATEGORIES, key=lambda x: x['priority'], reverse=True)
    
    # Find the first matching category
    for category in sorted_categories:
        for keyword in category['keywords']:
            if keyword.lower() in search_text:
                return category['id']
    
    # Return default category if no match
    return DEFAULT_CATEGORY['id']


def get_category_by_id(category_id: str) -> Dict[str, Any]:
    """Get category information by ID."""
    for category in SKILL_CATEGORIES:
        if category['id'] == category_id:
            return category
    return DEFAULT_CATEGORY


def get_all_categories() -> List[Dict[str, Any]]:
    """Get all categories including default."""
    return SKILL_CATEGORIES + [DEFAULT_CATEGORY]
