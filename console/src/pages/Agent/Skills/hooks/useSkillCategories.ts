/**
 * Hook for managing skill categories
 */

import { useState, useEffect, useCallback } from 'react';
import { categoriesApi } from '../../../../api/modules/categories';
import type { Category } from '../../../../api/types/category';

export function useSkillCategories() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadCategories = useCallback(async (enabledOnly = true) => {
    setLoading(true);
    setError(null);
    try {
      const data = await categoriesApi.getSkillCategories(enabledOnly);
      setCategories(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load categories');
      console.error('Failed to load skill categories:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const createCategory = async (category: Omit<Category, 'is_custom'>) => {
    try {
      const newCategory = await categoriesApi.createSkillCategory(category);
      await loadCategories();
      return newCategory;
    } catch (err) {
      console.error('Failed to create category:', err);
      throw err;
    }
  };

  const deleteCategory = async (categoryId: string) => {
    try {
      await categoriesApi.deleteSkillCategory(categoryId);
      await loadCategories();
    } catch (err) {
      console.error('Failed to delete category:', err);
      throw err;
    }
  };

  const toggleCategory = async (categoryId: string) => {
    try {
      await categoriesApi.toggleSkillCategory(categoryId);
      await loadCategories();
    } catch (err) {
      console.error('Failed to toggle category:', err);
      throw err;
    }
  };

  const reorderCategories = async (categoryIds: string[]) => {
    try {
      await categoriesApi.reorderSkillCategories(categoryIds);
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
