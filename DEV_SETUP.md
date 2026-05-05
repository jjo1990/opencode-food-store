# Development Environment Setup Guide

This guide walks you through setting up the Food Store v5.0 monorepo locally. Follow these steps and you'll have the entire stack (backend, frontend, database) running in under 10 minutes.

## Prerequisites

Before you start, ensure you have the following installed:

- **Node.js**: 18.0.0 or higher ([download](https://nodejs.org/))
- **npm**: 9.0.0 or higher (included with Node.js)
- **Python**: 3.11 or higher ([download](https://www.python.org/))
- **Docker Desktop**: Latest version ([download](https://www.docker.com/products/docker-desktop))
- **Git**: Latest version ([download](https://git-scm.com/))

### Verification

Check your versions:

```bash
node --version   # Should be v18.0.0 or higher
npm --version    # Should be 9.0.0 or higher
python --version # Should be 3.11.0 or higher
docker --version # Latest stable
git --version    # Latest stable
```

## First Time Setup

### 1. Clone the Repository

```bash
git clone https://github.com/food-store/food-store.git
cd food-store
```

### 2. Install Dependencies

```bash
npm install
```

This installs dependencies for all workspaces: frontend, backend, and shared packages.

### 3. Start Docker Services

```bash
docker-compose up
```

This will:

- Start PostgreSQL database (port 5432)
- Build and start the FastAPI backend (port 8000)
- Build and start the React frontend (port 3000)

The first run takes ~3-5 minutes as Docker images are built. Subsequent runs are instant.

### 4. Verify Everything is Running

Open your browser and navigate to:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs (Swagger UI)
- **Database**: Connect with your database client to `localhost:5432`

All services should be running without errors.

## Common Commands

### Development

```bash
# Start development servers (in separate terminals)
npm run dev

# Run tests in watch mode
npm run test:watch

# Check TypeScript types
npm run type-check

# Lint and check formatting
npm run lint
npm run format
```

### Docker

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Git & Pre-commit Hooks

```bash
# Make a commit (pre-commit hooks will run automatically)
git commit -m "feat: your message"

# If you need to bypass hooks (not recommended)
git commit -m "your message" --no-verify

# View pre-commit hook
cat .husky/pre-commit
```

### Testing

```bash
# Run all tests
npm run test

# Run frontend tests only
npm run test --workspace apps/frontend

# Run tests in watch mode
npm run test:watch

# Run backend tests
cd apps/backend && pytest

# Run with coverage
npm run test -- --coverage
```

## Troubleshooting

### Docker won't start

**Problem**: `Docker daemon is not running`

**Solution**:

- macOS: Open Docker.app from Applications
- Windows: Start Docker Desktop from Start Menu
- Linux: `sudo systemctl start docker`

### Ports in use

**Problem**: `bind: address already in use`

**Solution**:

```bash
# Find which process is using the port
lsof -i :3000      # Frontend
lsof -i :8000      # Backend
lsof -i :5432      # Database

# Kill the process (replace PID with the actual process ID)
kill -9 <PID>
```

### Database connection error

**Problem**: Backend can't connect to database

**Solution**:

```bash
# Ensure PostgreSQL is running
docker-compose ps

# Reset the database
docker-compose down -v
docker-compose up
```

### npm install fails

**Problem**: Dependency resolution errors

**Solution**:

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and lock file
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Tests fail unexpectedly

**Problem**: Tests pass locally but fail in CI

**Solution**:

```bash
# Ensure you're running the latest version of all packages
npm install

# Clear test cache
npm run test -- --clearCache

# Run tests with verbose output
npm run test -- --verbose
```

## Project Structure

```
food-store/
├── apps/
│   ├── frontend/              # React + TypeScript frontend (Vite)
│   │   ├── src/
│   │   │   ├── components/    # React components
│   │   │   ├── hooks/         # Custom React hooks
│   │   │   ├── utils/         # Utility functions
│   │   │   ├── types/         # TypeScript types
│   │   │   └── __tests__/     # Test files
│   │   ├── .eslintrc.json     # ESLint configuration
│   │   ├── jest.config.cjs    # Jest configuration
│   │   ├── tsconfig.json      # TypeScript configuration
│   │   ├── vite.config.ts     # Vite configuration
│   │   └── Dockerfile         # Docker build configuration
│   │
│   └── backend/               # FastAPI + Python backend
│       ├── app/
│       │   ├── main.py        # FastAPI app entry point
│       │   └── modules/       # Feature modules
│       ├── tests/
│       │   ├── unit/          # Unit tests
│       │   ├── integration/   # Integration tests
│       │   └── conftest.py    # Pytest fixtures
│       ├── pyproject.toml     # Python dependencies & config
│       ├── requirements.txt   # Pinned dependencies
│       └── Dockerfile         # Docker build configuration
│
├── packages/
│   ├── types/                 # Shared API types
│   ├── utils/                 # Shared utilities
│   └── config/                # Shared configuration
│
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI pipeline
│
├── .husky/                    # Git hooks configuration
│   ├── pre-commit             # Runs linting before commit
│   └── pre-push               # Runs tests before push
│
├── docker-compose.yml         # Production Docker setup
├── docker-compose.override.yml # Development overrides
├── .env.example               # Environment variables template
├── turbo.json                 # Turborepo configuration
├── tsconfig.json              # Root TypeScript config
├── .eslintrc.json             # Root ESLint configuration
└── .prettierrc.json           # Prettier formatting rules
```

## Development Conventions

### Naming Conventions

**Frontend (TypeScript/React)**:

- Files: camelCase (e.g., `userService.ts`, `Button.tsx`)
- Components: PascalCase (e.g., `UserProfile.tsx`)
- Functions: camelCase (e.g., `getUserById()`)
- Constants: UPPER_SNAKE_CASE (e.g., `API_URL`)

**Backend (Python/FastAPI)**:

- Files: snake_case (e.g., `user_service.py`, `user_model.py`)
- Functions: snake_case (e.g., `get_user_by_id()`)
- Classes: PascalCase (e.g., `UserService`)
- Constants: UPPER_SNAKE_CASE (e.g., `DATABASE_URL`)

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, perf, test, chore, ci

**Examples**:

```bash
git commit -m "feat(auth): add JWT token refresh endpoint"
git commit -m "fix(frontend): resolve pagination bug in user list"
git commit -m "docs: update installation guide"
git commit -m "refactor(backend): extract database layer"
```

### TypeScript Guidelines

- Use strict mode (`strict: true` in tsconfig.json)
- No implicit `any` types
- Prefer interfaces over types for object shapes
- Use descriptive names for generics
- Comment complex logic and business rules

### Python Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints on function signatures
- Write docstrings for public functions and classes
- Keep functions focused and small
- Use `async/await` for I/O operations

## Adding New Modules/Features

### Adding a Backend Module

```bash
# Create module structure
mkdir -p apps/backend/app/modules/users
touch apps/backend/app/modules/users/__init__.py
touch apps/backend/app/modules/users/models.py
touch apps/backend/app/modules/users/routes.py
touch apps/backend/app/modules/users/schemas.py
touch apps/backend/app/modules/users/service.py

# Create tests
mkdir -p apps/backend/tests/integration/users
touch apps/backend/tests/integration/users/test_user_routes.py
```

### Adding a Frontend Feature

```bash
# Create feature structure
mkdir -p apps/frontend/src/features/users
mkdir -p apps/frontend/src/features/users/components
mkdir -p apps/frontend/src/features/users/hooks
mkdir -p apps/frontend/src/features/users/__tests__

# Create files
touch apps/frontend/src/features/users/index.ts
touch apps/frontend/src/features/users/UserProfile.tsx
touch apps/frontend/src/features/users/__tests__/UserProfile.test.tsx
```

## CI/CD Pipeline

Our GitHub Actions pipeline runs on every push and PR:

1. **Lint** - ESLint + Ruff check code quality
2. **Type Check** - TypeScript type validation
3. **Tests** - Jest (frontend) + Pytest (backend)
4. **Build** - Build frontend and backend

All checks must pass before merging to main.

View workflow status: [GitHub Actions](https://github.com/food-store/food-store/actions)

## Getting Help

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Join team discussions on GitHub Discussions
- **Slack**: Reach out to the development team on Slack

## Next Steps

1. Read the [API Documentation](/docs/api.md)
2. Check out the [Frontend Architecture](/docs/frontend-architecture.md)
3. Review the [Backend Architecture](/docs/backend-architecture.md)
4. Start implementing your first feature!

Happy coding! 🚀
