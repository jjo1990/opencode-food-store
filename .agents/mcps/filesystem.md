# Filesystem MCP

**Model Context Protocol for File System Operations**

## Overview

This MCP provides efficient file system navigation, searching, and batch operations for the codebase.

## Features

- **File Search**: Glob patterns, regex content search
- **Bulk Operations**: Find, copy, move, delete across directories
- **Structure Analysis**: Directory tree, file counting
- **Content Search**: FTS5-based full-text search (via ripgrep)

## Configuration

### Search Patterns

**By Extension**:
```bash
**/*.ts      # All TypeScript files
**/*.tsx     # All React component files
**/*.py      # All Python files
**/*.md      # All Markdown docs
```

**By Directory**:
```bash
backend/**/*.py      # Python files in backend
frontend/src/**/*    # Frontend source
docs/**/*.md         # Documentation
openspec/specs/**/*  # Specification files
```

**By Name**:
```bash
**/test_*.py         # Python test files
**/*.test.ts         # TypeScript test files
**/index.ts          # All index files
```

## Common Operations

### Finding Files

```bash
# Find all TypeScript files
find . -name "*.ts" -o -name "*.tsx"

# Find all test files
find . -name "*.test.*" -o -name "test_*.py"

# Find configuration files
find . -name "*.config.*" -o -name "*.yml" -o -name "*.yaml"

# Find in specific directory
find backend -name "*.py" -type f
```

### Content Search

```bash
# Search for text in files
grep -r "pattern" .

# Search with regex
grep -r "^async def" backend/

# Search in specific file type
grep -r "import" backend/**/*.py

# Count matches
grep -r "pattern" . | wc -l

# Show file and line number
grep -rn "pattern" .
```

### Directory Structure

```bash
# Tree-like view
tree -L 2 -I 'node_modules|.git|__pycache__'

# Count files by type
find . -type f -name "*.py" | wc -l
find . -type f -name "*.ts" | wc -l

# Show directory sizes
du -sh backend/ frontend/

# Find large files
find . -type f -size +10M
```

## Project Structure

### Food Store Directory Map

```
food-store/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app instance
│   │   ├── api/               # Route handlers
│   │   ├── db/                # Database models and migrations
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   ├── tests/                 # Pytest test suite
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile
│
├── frontend/                   # React + Vite application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── store/             # Zustand state management
│   │   ├── services/          # API clients
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── Dockerfile
│
├── packages/                   # Shared packages (utils, types, etc)
│   ├── types/                 # Shared TypeScript types
│   └── utils/                 # Utility functions
│
├── docs/                       # Project documentation
│   ├── Descripcion.txt        # Vision and requirements
│   ├── Integrador.txt         # Architecture and design
│   └── Historias_de_usuario.txt # User stories
│
├── openspec/                   # OPSX artifacts
│   ├── changes/               # Active and archived changes
│   ├── specs/                 # Specification files (delta specs)
│   └── config.yaml            # OPSX configuration
│
├── .github/                    # GitHub configuration
│   ├── workflows/             # CI/CD pipelines
│   └── ISSUE_TEMPLATE/        # Issue templates
│
├── .agents/                    # Agent skills and MCPs
│   ├── skills/                # Installed skills
│   └── mcps/                  # Model Context Protocols
│
├── docker-compose.yml         # Local development stack
├── package.json               # Root monorepo config
├── turbo.json                 # Turbo build orchestration
└── README.md                  # Project overview
```

## Search Examples for Food Store

### Authentication Files (Phase 1)

```bash
# Find all auth-related files
find . -path ./node_modules -prune -o -name "*auth*" -type f -print

# Find JWT/token handlers
grep -r "jwt\|token" backend/app --include="*.py"

# Find role-based access control
grep -r "role\|permission" backend/app --include="*.py"
```

### Database Schema

```bash
# Find migration files
find backend -name "*.py" -path "*/migrations/*"

# Find model definitions
grep -r "class.*Model\|class.*Table" backend/app/db --include="*.py"

# Find database queries
grep -r "select\|where\|join" backend/app --include="*.py" | head -20
```

### Frontend Components

```bash
# Find React components
find frontend/src -name "*.tsx" -o -name "*.ts"

# Find hooks
find frontend/src -name "*Hook*" -o -path "*/hooks/*"

# Find tests
find frontend/src -name "*.test.*"

# Find styles
find frontend/src -name "*.css" -o -name "*.module.*"
```

### Documentation and Specs

```bash
# Find all markdown docs
find docs -name "*.md" -o -name "*.txt"

# Find OPSX specifications
find openspec -name "*.md"

# Find design documents
find openspec/changes -name "design.md"
```

## Integration with Development Workflow

### Before Starting a Phase

1. **Explore structure**: Find all related files
   ```bash
   find backend -name "*auth*" -o -path "*/api/*" -name "*.py"
   ```

2. **Search for patterns**: Understand existing code
   ```bash
   grep -r "def " backend/app/api --include="*.py" | head -10
   ```

3. **Check tests**: See testing patterns
   ```bash
   find backend/tests -name "*.py" -type f
   ```

### During Implementation

1. **Find TODO/FIXME**: Incomplete work
   ```bash
   grep -rn "TODO\|FIXME\|XXX" backend frontend
   ```

2. **Check imports**: Understand dependencies
   ```bash
   grep -n "^import\|^from" backend/app/main.py
   ```

3. **Find duplicates**: Refactoring candidates
   ```bash
   find . -name "*.py" -o -name "*.ts" | xargs wc -l | sort -rn | head -20
   ```

## When to Use This MCP

- ✅ Searching for files and patterns
- ✅ Understanding project structure
- ✅ Finding examples to follow
- ✅ Bulk file operations
- ✅ Code metrics and analysis
- ❌ Don't use for: Modifying files (use edit tool instead)

## Performance Tips

1. **Exclude directories**: `--exclude node_modules --exclude .git`
2. **Use specific patterns**: Narrow down search scope
3. **Limit results**: `head -n` for large result sets
4. **Cache results**: Save common searches

## See Also

- `README.md` — Project setup and conventions
- `.gitignore` — Files to exclude from searches
- `turbo.json` — Build configuration
