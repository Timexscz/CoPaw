/**
 * Tests for category API module.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { categoriesApi } from '../categories';

// Mock the request module
vi.mock('../../request', () => ({
  request: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('categoriesApi', () => {
  const { request } = await import('../../request');

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('listCategories', () => {
    it('should call GET /categories with type parameter', async () => {
      const mockResponse = [
        { id: 'database', name: '数据库', icon: '🗄️', color: '#722ed1' },
        { id: 'filesystem', name: '文件系统', icon: '📁', color: '#faad14' },
      ];
      vi.mocked(request.get).mockResolvedValue(mockResponse);

      const result = await categoriesApi.listCategories('mcp');

      expect(request.get).toHaveBeenCalledWith('/categories', { params: { type: 'mcp' } });
      expect(result).toEqual(mockResponse);
    });

    it('should handle skill categories', async () => {
      const mockResponse = [
        { id: 'documents', name: '文档处理', icon: '📄', color: '#1890ff' },
      ];
      vi.mocked(request.get).mockResolvedValue(mockResponse);

      const result = await categoriesApi.listCategories('skill');

      expect(request.get).toHaveBeenCalledWith('/categories', { params: { type: 'skill' } });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('createCategory', () => {
    it('should call POST /categories with category data', async () => {
      const mockResponse = {
        id: 'custom_123',
        name: 'Custom Category',
        icon: '🔌',
        color: '#13c2c2',
      };
      vi.mocked(request.post).mockResolvedValue(mockResponse);

      const result = await categoriesApi.createCategory('mcp', {
        id: 'custom_123',
        name: 'Custom Category',
        icon: '🔌',
        color: '#13c2c2',
        keywords: [],
        priority: 0,
        is_enabled: true,
        category_type: 'mcp',
      });

      expect(request.post).toHaveBeenCalledWith('/categories', {
        type: 'mcp',
        category: expect.objectContaining({
          id: 'custom_123',
          name: 'Custom Category',
        }),
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('updateCategory', () => {
    it('should call PUT /categories/:id with updated data', async () => {
      const mockResponse = {
        id: 'custom_123',
        name: 'Updated Category',
        icon: '🔧',
        color: '#52c41a',
      };
      vi.mocked(request.put).mockResolvedValue(mockResponse);

      const result = await categoriesApi.updateCategory('mcp', 'custom_123', {
        name: 'Updated Category',
        icon: '🔧',
        color: '#52c41a',
      });

      expect(request.put).toHaveBeenCalledWith('/categories/custom_123', {
        type: 'mcp',
        category: expect.objectContaining({
          name: 'Updated Category',
          icon: '🔧',
        }),
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('deleteCategory', () => {
    it('should call DELETE /categories/:id', async () => {
      const mockResponse = { success: true };
      vi.mocked(request.delete).mockResolvedValue(mockResponse);

      const result = await categoriesApi.deleteCategory('mcp', 'custom_123');

      expect(request.delete).toHaveBeenCalledWith('/categories/custom_123', {
        params: { type: 'mcp' },
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('toggleCategory', () => {
    it('should call PUT /categories/:id/toggle', async () => {
      const mockResponse = {
        id: 'custom_123',
        is_enabled: false,
      };
      vi.mocked(request.put).mockResolvedValue(mockResponse);

      const result = await categoriesApi.toggleCategory('mcp', 'custom_123', false);

      expect(request.put).toHaveBeenCalledWith('/categories/custom_123/toggle', {
        type: 'mcp',
        is_enabled: false,
      });
      expect(result.is_enabled).toBe(false);
    });
  });

  describe('reorderCategories', () => {
    it('should call PUT /categories/reorder with order array', async () => {
      const mockResponse = { success: true };
      const order = ['database', 'filesystem', 'api', 'ai'];
      vi.mocked(request.put).mockResolvedValue(mockResponse);

      const result = await categoriesApi.reorderCategories('mcp', order);

      expect(request.put).toHaveBeenCalledWith('/categories/reorder', {
        type: 'mcp',
        order,
      });
      expect(result).toEqual(mockResponse);
    });
  });
});
