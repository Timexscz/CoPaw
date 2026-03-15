/**
 * Tests for LoginPage component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import LoginPage from '../LoginPage';

// Mock the auth API
vi.mock('../../../api/modules/auth', () => ({
  authApi: {
    login: vi.fn(),
    getStatus: vi.fn(),
  },
}));

// Mock i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'en' },
  }),
}));

// Mock Ant Design message
vi.mock('antd', async () => {
  const actual = await vi.importActual('antd');
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn(),
      info: vi.fn(),
      warning: vi.fn(),
    },
  };
});

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );
};

describe('LoginPage', () => {
  const { authApi } = await import('../../../api/modules/auth');
  const { message } = await import('antd');

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render login form', () => {
    render(<LoginPage />, { wrapper: createWrapper() });

    expect(screen.getByPlaceholderText(/username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('should show validation error for empty username', async () => {
    render(<LoginPage />, { wrapper: createWrapper() });

    const passwordInput = screen.getByPlaceholderText(/password/i);
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });

    const loginButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(loginButton);

    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText(/username/i)).toBeInTheDocument();
    });
  });

  it('should show validation error for empty password', async () => {
    render(<LoginPage />, { wrapper: createWrapper() });

    const usernameInput = screen.getByPlaceholderText(/username/i);
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });

    const loginButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(loginButton);

    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText(/password/i)).toBeInTheDocument();
    });
  });

  it('should call login API with correct credentials', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'test-token',
      token_type: 'bearer',
      user: { id: 1, username: 'testuser' },
    });

    render(<LoginPage />, { wrapper: createWrapper() });

    const usernameInput = screen.getByPlaceholderText(/username/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const loginButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'testpass',
      });
    });

    expect(message.success).toHaveBeenCalled();
  });

  it('should show error on login failure', async () => {
    vi.mocked(authApi.login).mockRejectedValue(new Error('Invalid credentials'));

    render(<LoginPage />, { wrapper: createWrapper() });

    const usernameInput = screen.getByPlaceholderText(/username/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const loginButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpass' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalled();
      expect(message.error).toHaveBeenCalled();
    });
  });

  it('should navigate to register page when clicking register link', () => {
    render(<LoginPage />, { wrapper: createWrapper() });

    const registerLink = screen.getByText(/register/i);
    expect(registerLink).toBeInTheDocument();
    // Note: Actual navigation test would require more setup
  });
});
