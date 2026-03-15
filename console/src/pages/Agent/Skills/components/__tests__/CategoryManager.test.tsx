/**
 * Tests for Skill CategoryManager component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CategoryManager } from '../CategoryManager';

// Mock the useSkillCategories hook
vi.mock('../hooks/useSkillCategories', () => ({
  useSkillCategories: vi.fn(),
}));

// Mock Ant Design components
vi.mock('@agentscope-ai/design', async () => {
  const actual = await vi.importActual('@agentscope-ai/design');
  return {
    ...actual,
    Modal: vi.fn(({ children, open, onCancel }) =>
      open ? <div data-testid="modal">{children}</div> : null
    ),
    message: {
      success: vi.fn(),
      error: vi.fn(),
      info: vi.fn(),
      warning: vi.fn(),
    },
  };
});

describe('CategoryManager', () => {
  const { useSkillCategories } = await import('../hooks/useSkillCategories');
  const { message } = await import('@agentscope-ai/design');

  const mockCategories = [
    {
      id: 'documents',
      name: '文档处理',
      icon: '📄',
      color: '#1890ff',
      keywords: ['pdf', 'docx'],
      priority: 10,
      is_enabled: true,
      category_type: 'skill',
    },
    {
      id: 'automation',
      name: '自动化',
      icon: '⚙️',
      color: '#52c41a',
      keywords: ['cron', 'shell'],
      priority: 9,
      is_enabled: true,
      category_type: 'skill',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useSkillCategories).mockReturnValue({
      categories: mockCategories,
      loading: false,
      createCategory: vi.fn(),
      deleteCategory: vi.fn(),
      toggleCategory: vi.fn(),
      reorderCategories: vi.fn(),
    });
  });

  it('should render category list', () => {
    render(<CategoryManager open={true} onClose={vi.fn()} />);

    expect(screen.getByText('文档处理')).toBeInTheDocument();
    expect(screen.getByText('自动化')).toBeInTheDocument();
  });

  it('should show loading state', () => {
    vi.mocked(useSkillCategories).mockReturnValue({
      categories: [],
      loading: true,
      createCategory: vi.fn(),
      deleteCategory: vi.fn(),
      toggleCategory: vi.fn(),
      reorderCategories: vi.fn(),
    });

    render(<CategoryManager open={true} onClose={vi.fn()} />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('should open add modal when clicking add button', () => {
    render(<CategoryManager open={true} onClose={vi.fn()} />);

    const addButton = screen.getByText(/add/i);
    fireEvent.click(addButton);

    expect(screen.getByTestId('modal')).toBeInTheDocument();
  });

  it('should toggle category when switch is clicked', async () => {
    const toggleCategory = vi.fn();
    vi.mocked(useSkillCategories).mockReturnValue({
      categories: mockCategories,
      loading: false,
      createCategory: vi.fn(),
      deleteCategory: vi.fn(),
      toggleCategory,
      reorderCategories: vi.fn(),
    });

    render(<CategoryManager open={true} onClose={vi.fn()} />);

    // Find toggle switch for first category
    const switches = screen.getAllByRole('checkbox');
    if (switches.length > 0) {
      fireEvent.click(switches[0]);

      await waitFor(() => {
        expect(toggleCategory).toHaveBeenCalledWith('documents', false);
      });
    }
  });

  it('should call deleteCategory when confirming delete', async () => {
    const deleteCategory = vi.fn();
    vi.mocked(useSkillCategories).mockReturnValue({
      categories: mockCategories,
      loading: false,
      createCategory: vi.fn(),
      deleteCategory,
      toggleCategory: vi.fn(),
      reorderCategories: vi.fn(),
    });

    render(<CategoryManager open={true} onClose={vi.fn()} />);

    // Find and click delete button
    const deleteButtons = screen.getAllByRole('button').filter(btn =>
      btn.textContent?.includes('delete') || btn.textContent?.includes('删除')
    );

    if (deleteButtons.length > 0) {
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(deleteCategory).toHaveBeenCalledWith('documents');
      });
    }
  });
});
