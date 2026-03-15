/**
 * Tests for RegisterPage component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import RegisterPage from '../RegisterPage';

// Mock the auth API
vi.mock('../../../api/modules/auth', () => ({
  authApi: {
    register: vi.fn(),
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

describe('RegisterPage', () => {
  const { authApi } = await import('../../../api/modules/auth');
  const { message } = await import('antd');

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render registration form', () => {
    render(<RegisterPage />, { wrapper: createWrapper() });

    expect(screen.getByPlaceholderText(/username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/confirm.*password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
  });

  it('should show validation error for empty username', async () => {
    render(<RegisterPage />, { wrapper: createWrapper() });

    const passwordInput = screen.getByPlaceholderText(/password/i);
    fireEvent.change(passwordInput, { target: { value: 'testpass123' } });

    const confirmPasswordInput = screen.getByPlaceholderText(/confirm.*password/i);
    fireEvent.change(confirmPasswordInput, { target: { value: 'testpass123' } });

    const registerButton = screen.getByRole('button', { name: /register/i });
    fireEvent.click(registerButton);

    await waitFor(() => {
      expect(screen.getByText(/username/i)).toBeInTheDocument();
    });
  });

  it('should show error for mismatched passwords', async () => {
    render(<RegisterPage />, { wrapper: createWrapper() });

    const usernameInput = screen.getByPlaceholderText(/username/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const confirmPasswordInput = screen.getByPlaceholderText(/confirm.*password/i);

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'differentpass' } });

    const registerButton = screen.getByRole('button', { name: /register/i });
    fireEvent.click(registerButton);

    await waitFor(() => {
      expect(message.error).toHaveBeenCalled();
    });
  });

  it('should call register API with correct credentials', async () => {
    vi.mocked(authApi.register).mockResolvedValue({
      access_token: 'test-token',
      token_type: 'bearer',
      user: { id: 1, username: 'newuser' },
    });

    render(<RegisterPage />, { wrapper: createWrapper() });

    const usernameInput = screen.getByPlaceholderText(/username/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const confirmPasswordInput = screen.getByPlaceholderText(/confirm.*password/i);
    const registerButton = screen.getByRole('button', { name: /register/i });

    fireEvent.change(usernameInput, { target: { value: 'newuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'testpass123' } });
    fireEvent.click(registerButton);

    await waitFor(() => {
      expect(authApi.register).toHaveBeenCalledWith({
        username: 'newuser',
        password: 'testpass123',
      });
    });

    expect(message.success).toHaveBeenCalled();
  });

  it('should show error on registration failure', async () => {
    vi.mocked(authApi.register).mockRejectedValue(new Error('Username already exists'));

    render(<RegisterPage />, { wrapper: createWrapper() });

    const usernameInput = screen.getByPlaceholderText(/username/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const confirmPasswordInput = screen.getByPlaceholderText(/confirm.*password/i);
    const registerButton = screen.getByRole('button', { name: /register/i });

    fireEvent.change(usernameInput, { target: { value: 'existinguser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'testpass123' } });
    fireEvent.click(registerButton);

    await waitFor(() => {
      expect(authApi.register).toHaveBeenCalled();
      expect(message.error).toHaveBeenCalled();
    });
  });

  it('should navigate to login page when clicking login link', () => {
    render(<RegisterPage />, { wrapper: createWrapper() });

    const loginLink = screen.getByText(/login/i);
    expect(loginLink).toBeInTheDocument();
  });
});
