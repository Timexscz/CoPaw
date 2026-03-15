/**
 * Hook for managing MCP categories
 */

import { useState, useEffect, useCallback } from 'react';
import { categoriesApi } from '../../../../api/modules/categories';
import type { Category } from '../../../../api/types/category';

export function useMCPCategories() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadCategories = useCallback(async (enabledOnly = true) => {
    setLoading(true);
    setError(null);
    try {
      const data = await categoriesApi.getMCPCategories(enabledOnly);
      setCategories(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load categories');
      console.error('Failed to load MCP categories:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const createCategory = async (category: Omit<Category, 'is_custom'>) => {
    try {
      const newCategory = await categoriesApi.createMCPCategory(category);
      await loadCategories();
      return newCategory;
    } catch (err) {
      console.error('Failed to create category:', err);
      throw err;
    }
  };

  const deleteCategory = async (categoryId: string) => {
    try {
      await categoriesApi.deleteMCPCategory(categoryId);
      await loadCategories();
    } catch (err) {
      console.error('Failed to delete category:', err);
      throw err;
    }
  };

  const toggleCategory = async (categoryId: string) => {
    try {
      await categoriesApi.toggleMCPCategory(categoryId);
      await loadCategories();
    } catch (err) {
      console.error('Failed to toggle category:', err);
      throw err;
    }
  };

  const reorderCategories = async (categoryIds: string[]) => {
    try {
      await categoriesApi.reorderMCPCategories(categoryIds);
      // Optimistic update
      const newCategories = categoryIds.map(id => 
        categories.find(c => c.id === id)!
      ).map((cat, index) => ({
        ...cat,
        priority: categoryIds.length - index,
      }));
      setCategories(newCategories);
    } catch (err) {
      console.error('Failed to reorder categories:', err);
      throw err;
    }
  };

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  return {
    categories,
    loading,
    error,
    refreshCategories: loadCategories,
    createCategory,
    deleteCategory,
    toggleCategory,
    reorderCategories,
  };
}
