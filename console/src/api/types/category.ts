/**
 * Category type definitions
 */

export interface Category {
  id: string;
  name: string;
  icon: string;
  color: string;
  keywords: string[];
  priority: number;
  is_custom: boolean;
  is_enabled: boolean;
  category_type: 'skill' | 'mcp';
  matcher_type?: 'keyword' | 'transport';
  matcher_config?: {
    transport?: string[];
    keywords?: string[];
  };
}

export interface SkillCategoryAssignment {
  skill_name: string;
  category_id: string;
  ai_confidence?: number;
  is_manual?: boolean;
  matched_keywords?: string[];
}

export interface MCPCategoryAssignment {
  client_key: string;
  category_id: string;
  ai_confidence?: number;
  is_manual?: boolean;
  matched_keywords?: string[];
}
