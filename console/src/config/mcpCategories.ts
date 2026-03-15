/**
 * MCP Client Category Configuration
 * 
 * Supports user-defined categories with CRUD operations.
 */

export interface MCPCategoryRule {
  id: string;
  name: string;
  icon: string;
  color: string;
  matcher: (client: {
    name: string;
    description?: string;
    transport?: string;
    command?: string;
    url?: string;
    [key: string]: any;
  }) => boolean;
  priority: number;
  isCustom?: boolean;
  isEnabled: boolean;
}

// Note: matcher functions cannot be serialized, so we store them separately
interface SerializableMCPCategory extends Omit<MCPCategoryRule, 'matcher'> {
  matcherType: 'transport' | 'keyword' | 'custom';
  matcherConfig?: {
    transport?: string[];
    keywords?: string[];
  };
}

/**
 * Default built-in categories
 */
export const DEFAULT_MCP_CATEGORIES: MCPCategoryRule[] = [
  {
    id: 'database',
    name: '数据库',
    icon: '🗄️',
    color: '#722ed1',
    matcher: (client) => {
      const name = (client.name + ' ' + (client.description || '')).toLowerCase();
      return name.includes('postgres') || 
             name.includes('mysql') || 
             name.includes('sqlite') || 
             name.includes('mongo') || 
             name.includes('redis') ||
             name.includes('database') ||
             name.includes('sql');
    },
    priority: 10,
    isEnabled: true
  },
  {
    id: 'filesystem',
    name: '文件系统',
    icon: '📁',
    color: '#faad14',
    matcher: (client) => {
      const name = (client.name + ' ' + (client.description || '')).toLowerCase();
      return name.includes('file') || 
             name.includes('filesystem') || 
             name.includes('storage') ||
             name.includes('disk');
    },
    priority: 9,
    isEnabled: true
  },
  {
    id: 'api',
    name: 'API 集成',
    icon: '🔌',
    color: '#13c2c2',
    matcher: (client) => {
      const name = (client.name + ' ' + (client.description || '')).toLowerCase();
      return name.includes('api') || 
             name.includes('rest') || 
             name.includes('graphql') ||
             name.includes('webhook');
    },
    priority: 8,
    isEnabled: true
  },
  {
    id: 'ai',
    name: 'AI 服务',
    icon: '🤖',
    color: '#eb2f96',
    matcher: (client) => {
      const name = (client.name + ' ' + (client.description || '')).toLowerCase();
      return name.includes('llm') || 
             name.includes('model') || 
             name.includes('ai') ||
             name.includes('embedding') ||
             name.includes('chat') ||
             name.includes('openai') ||
             name.includes('anthropic');
    },
    priority: 7,
    isEnabled: true
  },
  {
    id: 'productivity',
    name: '效率工具',
    icon: '📊',
    color: '#2f54eb',
    matcher: (client) => {
      const name = (client.name + ' ' + (client.description || '')).toLowerCase();
      return name.includes('calendar') || 
             name.includes('todo') || 
             name.includes('task') ||
             name.includes('note') ||
             name.includes('notion') ||
             name.includes('slack');
    },
    priority: 6,
    isEnabled: true
  },
  {
    id: 'local',
    name: '本地服务',
    icon: '💻',
    color: '#1890ff',
    matcher: (client) => {
      return client.transport === 'stdio' || 
             (!client.transport && !!client.command);
    },
    priority: 5,
    isEnabled: true
  },
  {
    id: 'remote_http',
    name: '远程 HTTP',
    icon: '🌐',
    color: '#52c41a',
    matcher: (client) => {
      return client.transport === 'streamable_http' ||
             client.transport === 'http';
    },
    priority: 4,
    isEnabled: true
  },
  {
    id: 'remote_sse',
    name: '远程 SSE',
    icon: '📡',
    color: '#fa8c16',
    matcher: (client) => {
      return client.transport === 'sse';
    },
    priority: 3,
    isEnabled: true
  }
];

/**
 * Default category for MCP clients that don't match any rules
 */
export const DEFAULT_MCP_CATEGORY: MCPCategoryRule = {
  id: 'other',
  name: '其他',
  icon: '📦',
  color: '#d9d9d9',
  matcher: () => true,
  priority: 0,
  isEnabled: true
};

const STORAGE_KEY = 'mcp_custom_categories';

/**
 * Rebuild matcher function from config
 */
function buildMatcher(config: {
  matcherType: 'transport' | 'keyword' | 'custom';
  matcherConfig?: {
    transport?: string[];
    keywords?: string[];
  };
}): (client: any) => boolean {
  return (client) => {
    const name = (client.name + ' ' + (client.description || '')).toLowerCase();
    
    if (config.matcherType === 'transport' && config.matcherConfig?.transport) {
      return config.matcherConfig.transport.includes(client.transport);
    }
    
    if (config.matcherType === 'keyword' && config.matcherConfig?.keywords) {
      return config.matcherConfig.keywords.some(k => name.includes(k.toLowerCase()));
    }
    
    return false;
  };
}

/**
 * Load categories from localStorage or use defaults
 */
export function loadMCPCategories(): MCPCategoryRule[] {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const serializable = JSON.parse(saved) as SerializableMCPCategory[];
      // Rebuild matcher functions
      return serializable.map(cat => ({
        ...cat,
        matcher: buildMatcher(cat)
      }));
    }
  } catch (error) {
    console.error('Failed to load MCP categories:', error);
  }
  
  return [...DEFAULT_MCP_CATEGORIES];
}

/**
 * Save categories to localStorage
 */
export function saveMCPCategories(categories: MCPCategoryRule[]): void {
  try {
    // Convert to serializable format
    const serializable: SerializableMCPCategory[] = categories.map(cat => ({
      ...cat,
      matcherType: 'keyword',  // Default for custom categories
      matcherConfig: cat.isCustom ? {
        keywords: cat.matcher.toString().match(/includes\('([^']+)'/g)?.map(m => m.match(/'([^']+)'/)?.[1]).filter(Boolean) || []
      } : undefined
    } as SerializableMCPCategory));
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(serializable));
  } catch (error) {
    console.error('Failed to save MCP categories:', error);
  }
}

/**
 * Add a new custom category
 */
export function addMCPCategory(category: Omit<MCPCategoryRule, 'isCustom' | 'matcher' | 'id'> & {
  matcherType: 'transport' | 'keyword';
  matcherConfig: {
    transport?: string[];
    keywords?: string[];
  };
  id?: string;
}): MCPCategoryRule {
  const categories = loadMCPCategories();
  
  const newCategory: MCPCategoryRule = {
    ...category,
    matcher: buildMatcher({ matcherType: category.matcherType, matcherConfig: category.matcherConfig }),
    isCustom: true,
    id: category.id || `custom_${Date.now()}`
  };
  
  categories.push(newCategory);
  saveMCPCategories(categories);
  
  return newCategory;
}

/**
 * Update an existing category
 */
export function updateMCPCategory(categoryId: string, updates: Partial<MCPCategoryRule>): MCPCategoryRule | null {
  const categories = loadMCPCategories();
  const index = categories.findIndex(c => c.id === categoryId);
  
  if (index === -1) return null;
  
  categories[index] = { ...categories[index], ...updates };
  saveMCPCategories(categories);
  
  return categories[index];
}

/**
 * Delete a category (only custom categories can be deleted)
 */
export function deleteMCPCategory(categoryId: string): boolean {
  const categories = loadMCPCategories();
  const category = categories.find(c => c.id === categoryId);
  
  if (!category || !category.isCustom) {
    return false;
  }
  
  const filtered = categories.filter(c => c.id !== categoryId);
  saveMCPCategories(filtered);
  
  return true;
}

/**
 * Reorder categories by updating priorities
 */
export function reorderMCPCategories(categoryIds: string[]): void {
  const categories = loadMCPCategories();
  
  categoryIds.forEach((id, index) => {
    const category = categories.find(c => c.id === id);
    if (category) {
      category.priority = categoryIds.length - index;
    }
  });
  
  saveMCPCategories(categories);
}

/**
 * Enable/disable a category
 */
export function toggleMCPCategory(categoryId: string): boolean {
  const categories = loadMCPCategories();
  const category = categories.find(c => c.id === categoryId);
  
  if (!category) return false;
  
  category.isEnabled = !category.isEnabled;
  saveMCPCategories(categories);
  
  return true;
}

/**
 * Analyze MCP client and determine the best matching category
 */
export function categorizeMCP(client: {
  name: string;
  description?: string;
  transport?: string;
  command?: string;
  url?: string;
  [key: string]: any;
}): string {
  // First, check specialized categories (database, filesystem, etc.)
  const categories = loadMCPCategories().filter(c => c.isEnabled);
  const sortedCategories = [...categories].sort((a, b) => b.priority - a.priority);
  
  for (const category of sortedCategories) {
    if (category.matcher(client)) {
      return category.id;
    }
  }
  
  return DEFAULT_MCP_CATEGORY.id;
}

/**
 * Get category information by ID
 */
export function getMCPCategoryById(categoryId: string): MCPCategoryRule {
  const categories = loadMCPCategories();
  return categories.find(cat => cat.id === categoryId) || DEFAULT_MCP_CATEGORY;
}

/**
 * Get all enabled categories
 */
export function getEnabledMCPCategories(): MCPCategoryRule[] {
  return loadMCPCategories().filter(c => c.isEnabled);
}

/**
 * Get all categories including disabled ones
 */
export function getAllMCPCategories(): MCPCategoryRule[] {
  return loadMCPCategories();
}

/**
 * Get AI-powered category recommendations for MCP
 */
export function getAICategoryRecommendations(client: {
  name: string;
  description?: string;
  transport?: string;
  command?: string;
  url?: string;
}): Array<{ categoryId: string; confidence: number; reason: string }> {
  const categories = getEnabledMCPCategories();
  const recommendations: Array<{ categoryId: string; confidence: number; reason: string }> = [];
  
  for (const category of categories) {
    if (category.matcher(client)) {
      // Higher confidence for transport-based matches
      const isTransportMatch = category.id === 'local' || category.id === 'remote_http' || category.id === 'remote_sse';
      const confidence = isTransportMatch ? 90 : 70;
      
      recommendations.push({
        categoryId: category.id,
        confidence,
        reason: isTransportMatch 
          ? `基于传输方式：${client.transport || 'stdio'}`
          : `基于名称/描述匹配`
      });
    }
  }
  
  return recommendations.sort((a, b) => b.confidence - a.confidence).slice(0, 3);
}
