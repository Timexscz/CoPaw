# CoPaw Testing Guide

This document describes how to run tests for the CoPaw project.

## Test Structure

```
tests/
├── test_auth.py                    # Authentication unit tests
├── test_auth_integration.py        # Authentication API integration tests
├── test_categories.py              # Category management tests
├── e2e/
│   └── test_auth_flow.py           # End-to-end authentication flow tests
└── ...                             # Other existing tests

console/src/
├── api/modules/__tests__/
│   ├── auth.test.ts                # Auth API module tests
│   └── categories.test.ts          # Categories API module tests
├── pages/Auth/__tests__/
│   ├── LoginPage.test.tsx          # Login page component tests
│   └── RegisterPage.test.tsx       # Register page component tests
├── pages/Agent/MCP/components/__tests__/
│   └── MCPCategoryManager.test.tsx # MCP category manager tests
├── pages/Agent/Skills/components/__tests__/
│   └── CategoryManager.test.tsx    # Skill category manager tests
└── components/ThemeToggle/__tests__/
    └── ThemeToggle.test.tsx        # Theme toggle component tests
```

## Running Tests

### All Tests (Backend + Frontend)

```bash
# Using the test runner script
bash scripts/run_tests.sh
```

### Backend Tests (Python)

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_auth.py -v
pytest tests/test_auth_integration.py -v
pytest tests/test_categories.py -v

# Run with coverage
pytest --cov=copaw --cov-report=html

# Run E2E tests
pytest tests/e2e/test_auth_flow.py -v
```

### Frontend Tests (TypeScript/React)

```bash
cd console

# Install dependencies (if not already installed)
npm install

# Run all tests
npm run test

# Run tests in watch mode
npm run test -- --watch

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:ui

# Run specific test files
npm run test -- src/api/modules/__tests__/auth.test.ts
npm run test -- src/pages/Auth/__tests__/LoginPage.test.tsx
```

## Test Coverage

### Backend Coverage

```bash
# Generate coverage report
pytest --cov=copaw --cov-report=html --cov-report=term

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Frontend Coverage

```bash
cd console
npm run test:coverage

# Open coverage report
open coverage/index.html  # macOS
xdg-open coverage/index.html  # Linux
start coverage/index.html  # Windows
```

## Writing Tests

### Backend Tests (Python)

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test file for new feature.
"""

import pytest
from copaw.module import new_feature


class TestNewFeature:
    """Test new feature functionality."""

    def test_basic_functionality(self):
        """Test basic feature works."""
        result = new_feature.do_something()
        assert result is not None

    def test_with_parameters(self):
        """Test with different parameters."""
        result = new_feature.do_something(param="value")
        assert result == "expected"
```

### Frontend Tests (TypeScript/React)

```typescript
/**
 * Test file for new component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import NewComponent from '../NewComponent';

describe('NewComponent', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render correctly', () => {
    render(<NewComponent />);
    expect(screen.getByTestId('new-component')).toBeInTheDocument();
  });

  it('should handle user interaction', () => {
    render(<NewComponent />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(button).toHaveAttribute('aria-pressed', 'true');
  });
});
```

## Continuous Integration

Tests are automatically run in CI on:
- Every pull request
- Every push to main branch
- Before releases

### CI Configuration

- Backend: `.github/workflows/pre-commit.yml`
- Frontend: `.github/workflows/npm-format.yml`

## Troubleshooting

### Backend Test Issues

**Issue**: Tests fail with import errors
```bash
# Ensure package is installed in development mode
pip install -e ".[dev]"
```

**Issue**: Database connection errors
```bash
# Ensure PostgreSQL is running
sudo systemctl status postgresql

# Or use SQLite for testing
export TEST_DATABASE_URL="sqlite:///test.db"
```

### Frontend Test Issues

**Issue**: Tests fail with module not found
```bash
cd console
npm install
```

**Issue**: Tests fail with jsdom errors
```bash
# Ensure jsdom is installed
npm install --save-dev jsdom
```

## Test Best Practices

1. **Name tests clearly**: Use descriptive test names that explain what is being tested
2. **Test one thing per test**: Each test should verify a single behavior
3. **Use fixtures**: Reuse setup code with fixtures
4. **Mock external dependencies**: Don't test external services in unit tests
5. **Keep tests independent**: Tests should not depend on each other
6. **Run tests frequently**: Run tests locally before committing

## Coverage Goals

| Component | Current | Goal |
|-----------|---------|------|
| Backend (auth) | 85% | 90% |
| Backend (categories) | 80% | 90% |
| Frontend (auth) | 75% | 85% |
| Frontend (categories) | 70% | 85% |

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [Vitest documentation](https://vitest.dev/)
- [Testing Library documentation](https://testing-library.com/)
