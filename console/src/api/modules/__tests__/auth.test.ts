/**
 * Tests for authentication API module.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { authApi } from '../auth';

// Mock the request module
vi.mock('../../request', () => ({
  request: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

describe('authApi', () => {
  const { request } = await import('../../request');

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('login', () => {
    it('should call POST /auth/login with credentials', async () => {
      const mockResponse = {
        access_token: 'test-token',
        token_type: 'bearer',
        user: { id: 1, username: 'testuser' },
      };
      vi.mocked(request.post).mockResolvedValue(mockResponse);

      const result = await authApi.login({
        username: 'testuser',
        password: 'testpass',
      });

      expect(request.post).toHaveBeenCalledWith('/auth/login', {
        username: 'testuser',
        password: 'testpass',
      });
      expect(result).toEqual(mockResponse);
    });

    it('should handle login error', async () => {
      const error = new Error('Invalid credentials');
      vi.mocked(request.post).mockRejectedValue(error);

      await expect(
        authApi.login({
          username: 'testuser',
          password: 'wrongpass',
        })
      ).rejects.toThrow('Invalid credentials');
    });
  });

  describe('register', () => {
    it('should call POST /auth/register with user data', async () => {
      const mockResponse = {
        access_token: 'test-token',
        token_type: 'bearer',
        user: { id: 1, username: 'newuser' },
      };
      vi.mocked(request.post).mockResolvedValue(mockResponse);

      const result = await authApi.register({
        username: 'newuser',
        password: 'newpass',
      });

      expect(request.post).toHaveBeenCalledWith('/auth/register', {
        username: 'newuser',
        password: 'newpass',
      });
      expect(result).toEqual(mockResponse);
    });

    it('should handle registration error', async () => {
      const error = new Error('Username already exists');
      vi.mocked(request.post).mockRejectedValue(error);

      await expect(
        authApi.register({
          username: 'existinguser',
          password: 'newpass',
        })
      ).rejects.toThrow('Username already exists');
    });
  });

  describe('logout', () => {
    it('should call POST /auth/logout', async () => {
      const mockResponse = { message: 'Logged out successfully' };
      vi.mocked(request.post).mockResolvedValue(mockResponse);

      const result = await authApi.logout();

      expect(request.post).toHaveBeenCalledWith('/auth/logout');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getMe', () => {
    it('should call GET /auth/me', async () => {
      const mockResponse = { id: 1, username: 'testuser' };
      vi.mocked(request.get).mockResolvedValue(mockResponse);

      const result = await authApi.getMe();

      expect(request.get).toHaveBeenCalledWith('/auth/me');
      expect(result).toEqual(mockResponse);
    });

    it('should handle unauthenticated request', async () => {
      const error = new Error('Unauthorized');
      vi.mocked(request.get).mockRejectedValue(error);

      await expect(authApi.getMe()).rejects.toThrow('Unauthorized');
    });
  });

  describe('getStatus', () => {
    it('should call GET /auth/status', async () => {
      const mockResponse = {
        enabled: false,
        allow_registration: true,
        authenticated: false,
        user: null,
      };
      vi.mocked(request.get).mockResolvedValue(mockResponse);

      const result = await authApi.getStatus();

      expect(request.get).toHaveBeenCalledWith('/auth/status');
      expect(result).toEqual(mockResponse);
    });

    it('should return authenticated status', async () => {
      const mockResponse = {
        enabled: true,
        allow_registration: true,
        authenticated: true,
        user: { id: 1, username: 'testuser' },
      };
      vi.mocked(request.get).mockResolvedValue(mockResponse);

      const result = await authApi.getStatus();

      expect(result.authenticated).toBe(true);
      expect(result.user).toEqual({ id: 1, username: 'testuser' });
    });
  });
});
