/**
 * Skill Category Configuration
 * 
 * Supports user-defined categories with CRUD operations.
 * Categories are stored in localStorage for persistence.
 */

export interface SkillCategoryRule {
  id: string;
  name: string;
  icon: string;
  color: string;
  keywords: string[];
  priority: number;
  isCustom?: boolean;  // true if user-defined
  isEnabled: boolean;
}

/**
 * Default built-in categories
 */
export const DEFAULT_SKILL_CATEGORIES: SkillCategoryRule[] = [
  {
    id: 'document',
    name: '文档处理',
    icon: '📄',
    color: '#1890ff',
    keywords: [
      'docx', 'word', 'document', 'pdf', 'pptx', 'presentation', 
      'xlsx', 'excel', 'spreadsheet', 'file', 'text extraction',
      'create document', 'edit document', 'word document',
      '文档', '创建文档', '编辑文档', '提取文本'
    ],
    priority: 10,
    isEnabled: true
  },
  {
    id: 'communication',
    name: '通讯工具',
    icon: '📧',
    color: '#52c41a',
    keywords: [
      'email', 'imap', 'smtp', 'mail', 'message', 'send message',
      'dingtalk', 'discord', 'telegram', 'slack', 'chat',
      '邮件', '发消息', '钉钉', '通讯'
    ],
    priority: 9,
    isEnabled: true
  },
  {
    id: 'automation',
    name: '自动化',
    icon: '⚙️',
    color: '#fa8c16',
    keywords: [
      'cron', 'schedule', '定时', 'automation', 'automated',
      'task scheduler', 'periodic', 'recurring', 'interval',
      '定时任务', '计划任务', '自动化'
    ],
    priority: 9,
    isEnabled: true
  },
  {
    id: 'browser',
    name: '浏览器',
    icon: '🌐',
    color: '#722ed1',
    keywords: [
      'browser', 'web', 'http', 'url', 'navigate', 'click',
      'snapshot', 'page', 'headed', 'headless', 'selenium',
      '浏览器', '网页', '打开网址', '点击'
    ],
    priority: 9,
    isEnabled: true
  },
  {
    id: 'media',
    name: '媒体处理',
    icon: '🎵',
    color: '#eb2f96',
    keywords: [
      'audio', 'video', 'music', 'himalaya', 'podcast',
      'image', 'photo', 'picture', 'media', 'stream',
      '音频', '视频', '音乐', '媒体', '喜马拉雅'
    ],
    priority: 8,
    isEnabled: true
  },
  {
    id: 'news',
    name: '新闻资讯',
    icon: '📰',
    color: '#faad14',
    keywords: [
      'news', 'article', 'rss', 'feed', 'headline',
      '新闻', '资讯', '文章', '订阅'
    ],
    priority: 7,
    isEnabled: true
  },
  {
    id: 'lifestyle',
    name: '生活服务',
    icon: '🌟',
    color: '#13c2c2',
    keywords: [
      'weather', 'forecast', 'calendar', 'event', 'reminder',
      'shopping', 'food', 'restaurant', 'travel', 'hotel',
      '天气', '日历', '提醒', '购物', '美食', '旅游', '生活'
    ],
    priority: 6,
    isEnabled: true
  },
  {
    id: 'productivity',
    name: '效率工具',
    icon: '📊',
    color: '#2f54eb',
    keywords: [
      'note', 'todo', 'task', 'project', 'manage',
      'search', 'find', 'organize', 'productivity',
      '笔记', '待办', '任务', '管理', '搜索', '效率'
    ],
    priority: 6,
    isEnabled: true
  },
  {
    id: 'development',
    name: '开发工具',
    icon: '💻',
    color: '#52c41a',
    keywords: [
      'code', 'git', 'github', 'api', 'database',
      'sql', 'debug', 'test', 'deploy', 'build',
      '代码', '开发', '数据库', 'API', '测试'
    ],
    priority: 5,
    isEnabled: true
  },
  {
    id: 'ai',
    name: 'AI 工具',
    icon: '🤖',
    color: '#722ed1',
    keywords: [
      'llm', 'model', 'ai', 'chatbot', 'generate',
      'embedding', 'vector', 'ml', 'machine learning',
      '人工智能', '模型', '生成', '机器学习'
    ],
    priority: 5,
    isEnabled: true
  }
];

/**
 * Default category for skills that don't match any rules
 */
export const DEFAULT_CATEGORY: SkillCategoryRule = {
  id: 'other',
  name: '其他',
  icon: '📦',
  color: '#d9d9d9',
  keywords: [],
  priority: 0,
  isEnabled: true
};

const STORAGE_KEY = 'skills_custom_categories';

/**
 * Load categories from localStorage or use defaults
 */
export function loadSkillCategories(): SkillCategoryRule[] {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const customCategories = JSON.parse(saved) as SkillCategoryRule[];
      // Merge with defaults (custom categories override defaults)
      const defaultsMap = new Map(DEFAULT_SKILL_CATEGORIES.map(c => [c.id, c]));
      const merged: SkillCategoryRule[] = [];
      
      // Add custom/modified categories
      for (const custom of customCategories) {
        merged.push(custom);
        defaultsMap.delete(custom.id);
      }
      
      // Add remaining defaults
      merged.push(...defaultsMap.values());
      
      // Sort by priority
      return merged.sort((a, b) => b.priority - a.priority);
    }
  } catch (error) {
    console.error('Failed to load skill categories:', error);
  }
  
  return [...DEFAULT_SKILL_CATEGORIES].sort((a, b) => b.priority - a.priority);
}

/**
 * Save categories to localStorage
 */
export function saveSkillCategories(categories: SkillCategoryRule[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(categories));
  } catch (error) {
    console.error('Failed to save skill categories:', error);
  }
}

/**
 * Add a new custom category
 */
export function addSkillCategory(category: Omit<SkillCategoryRule, 'isCustom' | 'id'> & { id?: string }): SkillCategoryRule {
  const categories = loadSkillCategories();
  
  const newCategory: SkillCategoryRule = {
    ...category,
    isCustom: true,
    id: category.id || `custom_${Date.now()}`
  };
  
  categories.push(newCategory);
  saveSkillCategories(categories);
  
  return newCategory;
}

/**
 * Update an existing category
 */
export function updateSkillCategory(categoryId: string, updates: Partial<SkillCategoryRule>): SkillCategoryRule | null {
  const categories = loadSkillCategories();
  const index = categories.findIndex(c => c.id === categoryId);
  
  if (index === -1) return null;
  
  categories[index] = { ...categories[index], ...updates };
  saveSkillCategories(categories);
  
  return categories[index];
}

/**
 * Delete a category (only custom categories can be deleted)
 */
export function deleteSkillCategory(categoryId: string): boolean {
  const categories = loadSkillCategories();
  const category = categories.find(c => c.id === categoryId);
  
  if (!category || !category.isCustom) {
    return false;  // Can only delete custom categories
  }
  
  const filtered = categories.filter(c => c.id !== categoryId);
  saveSkillCategories(filtered);
  
  return true;
}

/**
 * Reorder categories by updating priorities
 */
export function reorderSkillCategories(categoryIds: string[]): void {
  const categories = loadSkillCategories();
  
  // Update priorities based on new order
  categoryIds.forEach((id, index) => {
    const category = categories.find(c => c.id === id);
    if (category) {
      category.priority = categoryIds.length - index;
    }
  });
  
  saveSkillCategories(categories);
}

/**
 * Enable/disable a category
 */
export function toggleSkillCategory(categoryId: string): boolean {
  const categories = loadSkillCategories();
  const category = categories.find(c => c.id === categoryId);
  
  if (!category) return false;
  
  category.isEnabled = !category.isEnabled;
  saveSkillCategories(categories);
  
  return true;
}

/**
 * Analyze skill content and determine the best matching category
 */
export function categorizeSkill(params: {
  name: string;
  description?: string;
  content?: string;
}): string {
  const { name, description = '', content = '' } = params;
  
  // Combine all text for analysis (lowercase for case-insensitive matching)
  const searchText = `${name} ${description} ${content}`.toLowerCase();
  
  // Load current categories and filter enabled ones
  const categories = loadSkillCategories().filter(c => c.isEnabled);
  
  // Sort by priority (highest first)
  const sortedCategories = [...categories].sort(
    (a, b) => b.priority - a.priority
  );
  
  // Find the first matching category
  for (const category of sortedCategories) {
    for (const keyword of category.keywords) {
      if (searchText.includes(keyword.toLowerCase())) {
        return category.id;
      }
    }
  }
  
  // Return default category if no match
  return DEFAULT_CATEGORY.id;
}

/**
 * Get category information by ID
 */
export function getCategoryById(categoryId: string): SkillCategoryRule {
  const categories = loadSkillCategories();
  return categories.find(cat => cat.id === categoryId) || DEFAULT_CATEGORY;
}

/**
 * Get all enabled categories (for filter dropdowns, etc.)
 */
export function getEnabledCategories(): SkillCategoryRule[] {
  return loadSkillCategories().filter(c => c.isEnabled);
}

/**
 * Get all categories including disabled ones (for management UI)
 */
export function getAllCategories(): SkillCategoryRule[] {
  return loadSkillCategories();
}

/**
 * Generate AI-powered category recommendations
 * This is a simple heuristic-based approach
 * For real AI, you could call an LLM API
 */
export function getAICategoryRecommendations(params: {
  name: string;
  description?: string;
  content?: string;
}): Array<{ categoryId: string; confidence: number; reason: string }> {
  const { name, description = '', content = '' } = params;
  const searchText = `${name} ${description} ${content}`.toLowerCase();
  
  const categories = getEnabledCategories();
  const recommendations: Array<{ categoryId: string; confidence: number; reason: string }> = [];
  
  for (const category of categories) {
    let matchCount = 0;
    const matchedKeywords: string[] = [];
    
    for (const keyword of category.keywords) {
      if (searchText.includes(keyword.toLowerCase())) {
        matchCount++;
        matchedKeywords.push(keyword);
      }
    }
    
    if (matchCount > 0) {
      // Calculate confidence based on number of matched keywords
      const confidence = Math.min(100, matchCount * 15);
      recommendations.push({
        categoryId: category.id,
        confidence,
        reason: `匹配关键词：${matchedKeywords.slice(0, 3).join(', ')}${matchedKeywords.length > 3 ? '...' : ''}`
      });
    }
  }
  
  // Sort by confidence
  return recommendations.sort((a, b) => b.confidence - a.confidence).slice(0, 3);
}
