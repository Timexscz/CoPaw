/**
 * Tests for ThemeToggle component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ThemeToggle from '../ThemeToggle';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock Ant Design Switch
vi.mock('antd', async () => {
  const actual = await vi.importActual('antd');
  return {
    ...actual,
    Switch: vi.fn(({ checked, onChange, checkedChildren, unCheckedChildren }) => (
      <button
        data-testid="theme-toggle"
        onClick={() => onChange(!checked)}
        aria-pressed={checked}
      >
        {checked ? checkedChildren : unCheckedChildren}
      </button>
    ),
  };
});

describe('ThemeToggle', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  it('should render theme toggle', () => {
    render(<ThemeToggle />);

    expect(screen.getByTestId('theme-toggle')).toBeInTheDocument();
  });

  it('should default to light mode', () => {
    render(<ThemeToggle />);

    const toggle = screen.getByTestId('theme-toggle');
    expect(toggle).toHaveAttribute('aria-pressed', 'false');
  });

  it('should toggle to dark mode when clicked', () => {
    render(<ThemeToggle />);

    const toggle = screen.getByTestId('theme-toggle');
    fireEvent.click(toggle);

    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'dark');
  });

  it('should read theme from localStorage', () => {
    localStorageMock.getItem.mockReturnValue('dark');

    render(<ThemeToggle />);

    const toggle = screen.getByTestId('theme-toggle');
    expect(toggle).toHaveAttribute('aria-pressed', 'true');
  });

  it('should apply dark theme class to document', () => {
    render(<ThemeToggle />);

    const toggle = screen.getByTestId('theme-toggle');
    fireEvent.click(toggle);

    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('should toggle back to light mode', () => {
    localStorageMock.getItem.mockReturnValue('dark');

    render(<ThemeToggle />);

    const toggle = screen.getByTestId('theme-toggle');
    fireEvent.click(toggle);

    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });
});
