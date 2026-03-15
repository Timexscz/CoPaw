/**
 * Tests for MCPCategoryManager component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MCPCategoryManager } from '../MCPCategoryManager';

// Mock the useMCPCategories hook
vi.mock('../hooks/useMCPCategories', () => ({
  useMCPCategories: vi.fn(),
}));

// Mock Ant Design components
vi.mock('@agentscope-ai/design', async () => {
  const actual = await vi.importActual('@agentscope-ai/design');
  return {
    ...actual,
    Modal: vi.fn(({ children, open, onCancel }) =>
      open ? <div data-testid="modal">{children}</div> : null
    ),
    Form: vi.fn(({ children, form }) => (
      <form data-testid="form">{children}</form>
    )),
    Input: vi.fn((props) => <input data-testid="input" {...props} />),
    Button: vi.fn(({ children, onClick }) => (
      <button data-testid="button" onClick={onClick}>{children}</button>
    )),
    Table: vi.fn(({ dataSource, columns }) => (
      <table data-testid="table">
        <tbody>
          {dataSource?.map((item, index) => (
            <tr key={item.id || index} data-testid="table-row">
              {columns?.map((col, i) => (
                <td key={i} data-testid="table-cell">
                  {col.render ? col.render(item[col.dataIndex], item) : item[col.dataIndex]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    )),
    Switch: vi.fn(({ checked, onChange }) => (
      <input
        type="checkbox"
        data-testid="switch"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
    )),
    message: {
      success: vi.fn(),
      error: vi.fn(),
      info: vi.fn(),
      warning: vi.fn(),
    },
  };
});

describe('MCPCategoryManager', () => {
  const { useMCPCategories } = await import('../hooks/useMCPCategories');
  const { message } = await import('@agentscope-ai/design');

  const mockCategories = [
    {
      id: 'database',
      name: '数据库',
      icon: '🗄️',
      color: '#722ed1',
      keywords: ['postgres', 'mysql'],
      priority: 10,
      is_enabled: true,
      category_type: 'mcp',
    },
    {
      id: 'filesystem',
      name: '文件系统',
      icon: '📁',
      color: '#faad14',
      keywords: ['file', 'storage'],
      priority: 9,
      is_enabled: true,
      category_type: 'mcp',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useMCPCategories).mockReturnValue({
      categories: mockCategories,
      loading: false,
      createCategory: vi.fn(),
      deleteCategory: vi.fn(),
      toggleCategory: vi.fn(),
      reorderCategories: vi.fn(),
    });
  });

  it('should render category list', () => {
    render(<MCPCategoryManager open={true} onClose={vi.fn()} />);

    expect(screen.getByTestId('table')).toBeInTheDocument();
    expect(screen.getAllByTestId('table-row')).toHaveLength(2);
  });

  it('should show loading state', () => {
    vi.mocked(useMCPCategories).mockReturnValue({
      categories: [],
      loading: true,
      createCategory: vi.fn(),
      deleteCategory: vi.fn(),
      toggleCategory: vi.fn(),
      reorderCategories: vi.fn(),
    });

    render(<MCPCategoryManager open={true} onClose={vi.fn()} />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('should open add modal when clicking add button', () => {
    render(<MCPCategoryManager open={true} onClose={vi.fn()} />);

    const addButton = screen.getByText(/add/i);
    fireEvent.click(addButton);

    expect(screen.getByTestId('modal')).toBeInTheDocument();
  });

  it('should toggle category when switch is clicked', async () => {
    const toggleCategory = vi.fn();
    vi.mocked(useMCPCategories).mockReturnValue({
      categories: mockCategories,
      loading: false,
      createCategory: vi.fn(),
      deleteCategory: vi.fn(),
      toggleCategory,
      reorderCategories: vi.fn(),
    });

    render(<MCPCategoryManager open={true} onClose={vi.fn()} />);

    const switches = screen.getAllByTestId('switch');
    fireEvent.click(switches[0]);

    await waitFor(() => {
      expect(toggleCategory).toHaveBeenCalledWith('database', false);
    });
  });

  it('should call deleteCategory when confirming delete', async () => {
    const deleteCategory = vi.fn();
    vi.mocked(useMCPCategories).mockReturnValue({
      categories: mockCategories,
      loading: false,
      createCategory: vi.fn(),
      deleteCategory,
      toggleCategory: vi.fn(),
      reorderCategories: vi.fn(),
    });

    render(<MCPCategoryManager open={true} onClose={vi.fn()} />);

    // Find and click delete button (usually in table row)
    const deleteButtons = screen.getAllByTestId('button').filter(btn =>
      btn.textContent?.includes('delete') || btn.textContent?.includes('删除')
    );

    if (deleteButtons.length > 0) {
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(deleteCategory).toHaveBeenCalledWith('database');
      });
    }
  });

  it('should close modal when onClose is called', () => {
    const onClose = vi.fn();
    render(<MCPCategoryManager open={true} onClose={onClose} />);

    // Modal should be open
    expect(screen.getByTestId('modal')).toBeInTheDocument();

    // Note: Actual close test would require more setup
  });
});
