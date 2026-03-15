/**
 * Categories API module
 */

import { request } from '../request';
import type { Category } from '../types/category';

export const categoriesApi = {
  /**
   * Get skill categories
   */
  getSkillCategories: (enabledOnly = true) =>
    request<Category[]>(`/categories/skills?enabled_only=${enabledOnly}`),

  /**
   * Get MCP categories
   */
  getMCPCategories: (enabledOnly = true) =>
    request<Category[]>(`/categories/mcp?enabled_only=${enabledOnly}`),

  /**
   * Create a new skill category
   */
  createSkillCategory: (category: Omit<Category, 'is_custom'>) =>
    request<Category>('/categories/skills', {
      method: 'POST',
      body: JSON.stringify(category),
    }),

  /**
   * Create a new MCP category
   */
  createMCPCategory: (category: Omit<Category, 'is_custom'>) =>
    request<Category>('/categories/mcp', {
      method: 'POST',
      body: JSON.stringify(category),
    }),

  /**
   * Reorder skill categories
   */
  reorderSkillCategories: (categoryIds: string[]) =>
    request('/categories/skills/reorder', {
      method: 'PUT',
      body: JSON.stringify({ category_ids: categoryIds }),
    }),

  /**
   * Reorder MCP categories
   */
  reorderMCPCategories: (categoryIds: string[]) =>
    request('/categories/mcp/reorder', {
      method: 'PUT',
      body: JSON.stringify({ category_ids: categoryIds }),
    }),

  /**
   * Delete a skill category
   */
  deleteSkillCategory: (categoryId: string) =>
    request(`/categories/skills/${categoryId}`, { method: 'DELETE' }),

  /**
   * Delete an MCP category
   */
  deleteMCPCategory: (categoryId: string) =>
    request(`/categories/mcp/${categoryId}`, { method: 'DELETE' }),

  /**
   * Toggle skill category enabled status
   */
  toggleSkillCategory: (categoryId: string) =>
    request(`/categories/skills/${categoryId}/toggle`, { method: 'PATCH' }),

  /**
   * Toggle MCP category enabled status
   */
  toggleMCPCategory: (categoryId: string) =>
    request(`/categories/mcp/${categoryId}/toggle`, { method: 'PATCH' }),

  /**
   * Set category for a skill (manual assignment)
   */
  setSkillCategory: (skillName: string, categoryId: string) =>
    request(`/categories/skills/${skillName}/category`, {
      method: 'POST',
      body: JSON.stringify({ category_id: categoryId }),
    }),

  /**
   * Get category for a skill
   */
  getSkillCategory: (skillName: string) =>
    request<{ category_id: string }>(`/categories/skills/${skillName}/category`),

  /**
   * Batch get categories for multiple skills
   */
  batchGetSkillCategories: (skillNames: string[]) =>
    request<Record<string, string>>('/categories/skills/batch/categorize', {
      method: 'POST',
      body: JSON.stringify({ skill_names: skillNames }),
    }),

  /**
   * Get skill detail with Markdown content
   */
  getSkillDetail: (skillName: string) =>
    request<{
      name: string;
      source: string;
      path: string;
      metadata: Record<string, any>;
      category: string;
      category_name: string;
      category_icon: string;
      category_color: string;
      html_content: string;
      raw_content: string;
    }>(`/skills/${skillName}/detail`),
};
