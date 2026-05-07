# React Testing Skill

**Patterns and best practices for testing React components and hooks with Jest and React Testing Library**

## Overview

This skill provides comprehensive guidance for unit and integration testing of React components, hooks, and state management using Jest and React Testing Library.

## Testing Framework Setup

### Dependencies (already in `package.json`)

```json
{
  "devDependencies": {
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "@testing-library/user-event": "^14.5.0",
    "ts-jest": "^29.1.0"
  }
}
```

### Configuration

**File**: `frontend/jest.config.cjs`

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts?(x)', '**/?(*.)+(spec|test).ts?(x)'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  setupFilesAfterEnv: ['<rootDir>/src/__tests__/setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/main.tsx',
  ],
};
```

**File**: `frontend/src/__tests__/setup.ts`

```typescript
import '@testing-library/jest-dom';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Suppress console errors in tests
global.console.error = jest.fn();
global.console.warn = jest.fn();
```

## Test Patterns

### 1. Component Rendering Tests

**Pattern**: Test that component renders correctly with props

```typescript
// File: frontend/src/__tests__/Button.test.tsx

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Button from '@/components/Button';

describe('Button Component', () => {
  it('renders with default label', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('renders with custom className', () => {
    render(<Button className="custom-btn">Click</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('custom-btn');
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('renders loading state', () => {
    render(<Button isLoading>Click</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('renders with icon', () => {
    const { container } = render(
      <Button icon={<span data-testid="icon">⭐</span>}>
        Star
      </Button>
    );
    expect(screen.getByTestId('icon')).toBeInTheDocument();
  });
});
```

### 2. User Interaction Tests

**Pattern**: Simulate user actions and verify behavior

```typescript
// File: frontend/src/__tests__/LoginForm.test.tsx

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginForm from '@/components/LoginForm';

describe('LoginForm Component', () => {
  it('calls onSubmit with form data when submitted', async () => {
    const user = userEvent.setup();
    const handleSubmit = jest.fn();
    
    render(<LoginForm onSubmit={handleSubmit} />);
    
    // Fill form
    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    
    // Submit
    await user.click(screen.getByRole('button', { name: /login/i }));
    
    // Verify
    expect(handleSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123',
    });
  });

  it('shows validation errors', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={jest.fn()} />);
    
    // Try to submit empty form
    await user.click(screen.getByRole('button', { name: /login/i }));
    
    // Verify error messages
    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    expect(screen.getByText(/password is required/i)).toBeInTheDocument();
  });

  it('disables submit button during submission', async () => {
    const user = userEvent.setup();
    const handleSubmit = jest.fn(
      () => new Promise(resolve => setTimeout(resolve, 1000))
    );
    
    render(<LoginForm onSubmit={handleSubmit} />);
    
    // Fill and submit
    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /login/i }));
    
    // Button should be disabled during submission
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### 3. Hook Testing

**Pattern**: Test custom React hooks with renderHook

```typescript
// File: frontend/src/__tests__/useAuth.test.ts

import { renderHook, act } from '@testing-library/react';
import useAuth from '@/hooks/useAuth';

describe('useAuth Hook', () => {
  it('initializes with no user', () => {
    const { result } = renderHook(() => useAuth());
    expect(result.current.user).toBeNull();
    expect(result.current.isLoading).toBe(false);
  });

  it('logs in user successfully', async () => {
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      await result.current.login('test@example.com', 'password123');
    });
    
    expect(result.current.user).toBeDefined();
    expect(result.current.user?.email).toBe('test@example.com');
  });

  it('handles login errors', async () => {
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      try {
        await result.current.login('wrong@example.com', 'wrongpassword');
      } catch (error) {
        // Error expected
      }
    });
    
    expect(result.current.user).toBeNull();
    expect(result.current.error).toBeDefined();
  });

  it('logs out user', async () => {
    const { result } = renderHook(() => useAuth());
    
    // Login
    await act(async () => {
      await result.current.login('test@example.com', 'password123');
    });
    
    // Logout
    await act(async () => {
      await result.current.logout();
    });
    
    expect(result.current.user).toBeNull();
  });
});
```

### 4. State Management Testing (Zustand)

**Pattern**: Test Zustand store mutations and selectors

```typescript
// File: frontend/src/__tests__/authStore.test.ts

import { renderHook, act } from '@testing-library/react';
import useAuthStore from '@/store/authStore';

describe('Auth Store', () => {
  beforeEach(() => {
    // Reset store before each test
    useAuthStore.getState().reset();
  });

  it('initializes with empty state', () => {
    const { result } = renderHook(() => useAuthStore());
    expect(result.current.user).toBeNull();
    expect(result.current.tokens).toBeNull();
  });

  it('sets user and tokens on login', () => {
    const { result } = renderHook(() => useAuthStore());
    
    act(() => {
      result.current.setUser({
        id: '1',
        email: 'test@example.com',
        role: 'user',
      });
      result.current.setTokens({
        accessToken: 'access_token_123',
        refreshToken: 'refresh_token_456',
      });
    });
    
    expect(result.current.user?.email).toBe('test@example.com');
    expect(result.current.tokens?.accessToken).toBe('access_token_123');
  });

  it('clears user and tokens on logout', () => {
    const { result } = renderHook(() => useAuthStore());
    
    act(() => {
      result.current.setUser({
        id: '1',
        email: 'test@example.com',
        role: 'user',
      });
    });
    
    expect(result.current.user).toBeDefined();
    
    act(() => {
      result.current.reset();
    });
    
    expect(result.current.user).toBeNull();
    expect(result.current.tokens).toBeNull();
  });

  it('selects only required state', () => {
    const { result: fullResult } = renderHook(() => useAuthStore());
    const { result: userResult } = renderHook(() => 
      useAuthStore(state => state.user)
    );
    
    act(() => {
      fullResult.current.setUser({
        id: '1',
        email: 'test@example.com',
        role: 'user',
      });
    });
    
    expect(userResult.current?.email).toBe('test@example.com');
  });
});
```

### 5. API Mock Testing

**Pattern**: Mock API calls with jest and test component with mocked data

```typescript
// File: frontend/src/__tests__/UserProfile.test.tsx

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UserProfile from '@/components/UserProfile';
import * as api from '@/services/api';

jest.mock('@/services/api');

describe('UserProfile Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches and displays user data', async () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
    };
    
    (api.getUser as jest.Mock).mockResolvedValue(mockUser);
    
    render(<UserProfile userId="1" />);
    
    // Loading state
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    
    // Data loaded
    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    (api.getUser as jest.Mock).mockRejectedValue(
      new Error('Failed to fetch user')
    );
    
    render(<UserProfile userId="1" />);
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('refetches data when userId changes', async () => {
    const mockUser1 = { id: '1', name: 'User 1' };
    const mockUser2 = { id: '2', name: 'User 2' };
    
    (api.getUser as jest.Mock)
      .mockResolvedValueOnce(mockUser1)
      .mockResolvedValueOnce(mockUser2);
    
    const { rerender } = render(<UserProfile userId="1" />);
    
    await waitFor(() => {
      expect(screen.getByText('User 1')).toBeInTheDocument();
    });
    
    rerender(<UserProfile userId="2" />);
    
    await waitFor(() => {
      expect(screen.getByText('User 2')).toBeInTheDocument();
    });
    
    expect(api.getUser).toHaveBeenCalledTimes(2);
  });
});
```

## Test Organization

### Directory Structure

```
frontend/src/
├── __tests__/
│   ├── setup.ts                    # Jest setup
│   ├── components/
│   │   ├── Button.test.tsx
│   │   ├── LoginForm.test.tsx
│   │   └── UserProfile.test.tsx
│   ├── hooks/
│   │   ├── useAuth.test.ts
│   │   ├── useFetch.test.ts
│   │   └── useCart.test.ts
│   ├── store/
│   │   ├── authStore.test.ts
│   │   ├── cartStore.test.ts
│   │   └── userStore.test.ts
│   └── services/
│       └── api.test.ts
├── components/
├── hooks/
├── store/
└── services/
```

## Running Tests

### All Tests
```bash
npm test
```

### Watch Mode
```bash
npm run test:watch
```

### With Coverage
```bash
npm test -- --coverage
```

### Specific Test File
```bash
npm test -- Button.test.tsx
```

### Specific Test
```bash
npm test -- Button.test.tsx -t "renders with custom className"
```

## Testing Queries (React Testing Library)

### Priority (Most to Least)

1. **Accessible Queries** (RECOMMENDED)
   ```typescript
   screen.getByRole('button', { name: /submit/i })
   screen.getByLabelText(/password/i)
   screen.getByDisplayValue('John')
   ```

2. **Semantic Queries**
   ```typescript
   screen.getByAltText('profile')
   screen.getByTitle('close')
   ```

3. **Text Content**
   ```typescript
   screen.getByText(/welcome/i)
   ```

4. **Test IDs** (LAST RESORT)
   ```typescript
   screen.getByTestId('custom-element')
   ```

## Best Practices

### 1. Use User Events Over Fireevents
```typescript
// ✅ Good
await user.click(button);
await user.type(input, 'text');

// ❌ Bad
fireEvent.click(button);
```

### 2. Avoid Testing Implementation Details
```typescript
// ❌ Bad - Testing internal state
expect(component.state.isOpen).toBe(true);

// ✅ Good - Testing user-visible behavior
expect(screen.getByRole('menu')).toBeVisible();
```

### 3. Use waitFor for Async Operations
```typescript
// ✅ Good
await waitFor(() => {
  expect(screen.getByText('Data loaded')).toBeInTheDocument();
});

// ❌ Bad - Race condition
expect(screen.getByText('Data loaded')).toBeInTheDocument();
```

### 4. Mock External Dependencies
```typescript
// ✅ Good
jest.mock('@/services/api');

// ❌ Bad - Making real API calls in tests
```

### 5. Descriptive Test Names
```typescript
// ✅ Good
it('shows validation error when email is invalid', () => { ... });

// ❌ Bad
it('validates email', () => { ... });
```

## Coverage Goals (Phase 1 - Frontend)

- **Components**: 80%+ coverage
- **Hooks**: 90%+ coverage
- **Stores**: 95%+ coverage
- **Critical Paths**: 100% coverage

## Integration with Food Store Phase 1

### Critical Test Cases (Authentication)

- ✅ LoginForm component renders and submits
- ✅ LoginForm validates email/password
- ✅ useAuth hook manages login/logout
- ✅ Protected routes redirect unauthenticated users
- ✅ Auth store persists tokens
- ✅ API calls include auth headers
- ✅ Token refresh on expiration
- ✅ Error messages display correctly

### Test Execution in CI/CD

In `.github/workflows/test.yml`:
```yaml
- name: Run React Tests
  run: |
    cd frontend
    npm test -- --coverage
```

## Debugging Tips

### 1. Debug Output
```typescript
import { render, screen } from '@testing-library/react';

render(<MyComponent />);
screen.debug(); // Prints DOM
```

### 2. Specific Element Debug
```typescript
const button = screen.getByRole('button');
screen.debug(button); // Prints just that element
```

### 3. React DevTools in Tests
```typescript
import '@testing-library/jest-dom/extend-expect';

// Use debugger
render(<MyComponent />);
debugger; // Pauses execution
```

## See Also

- `frontend/jest.config.cjs` — Jest configuration
- `frontend/package.json` — Test dependencies
- `frontend/src/__tests__/setup.ts` — Test setup
- `docs/Historias_de_usuario.txt` — User stories for test acceptance criteria
