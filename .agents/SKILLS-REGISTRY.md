# Food Store Skills & MCPs Registry

**Comprehensive registry of all installed skills and MCPs for the Food Store v5.0 project**

## Overview

This registry documents all available skills (specialized agent instructions) and MCPs (Model Context Protocols) for the Food Store project, enabling consistent patterns and best practices across the codebase.

---

## 🎯 Skills (Installed)

Skills provide specialized instructions and patterns for specific tasks.

### System Skills (Installed)

| Skill              | Location                      | Purpose                                         |
| ------------------ | ----------------------------- | ----------------------------------------------- |
| **find-skills**    | `.agents/skills/find-skills/` | Discover and install new agent skills           |
| **branch-pr**      | Global                        | GitHub PR creation workflow                     |
| **issue-creation** | Global                        | GitHub issue management                         |
| **openspec-\***    | Global                        | OPSX workflow (propose, apply, archive, verify) |
| **judgment-day**   | Global                        | Adversarial review protocol                     |

### Project Skills (Custom)

#### 1. **Frontend Design**

- **Location**: `.agents/skills/frontend-design/SKILL.md`
- **Purpose**: FSD structure, React components, TanStack Query, Zustand, Tailwind, Axios patterns
- **Coverage**: Component lifecycle (loading/error/empty/data), URL state sync, entity types, API modules
- **Key Files**: `frontend/src/`
- **When to Use**: Creating/modifying any React component, hook, store, or page
- **Example**: Catalog page with filters, product detail, shared UI components

#### 2. **FastAPI Testing**

- **Location**: `.agents/skills/fastapi-testing/SKILL.md`
- **Purpose**: Unit, integration, E2E testing patterns for FastAPI
- **Coverage**: Pytest fixtures, mocking, async testing, database fixtures
- **Key Files**: `backend/tests/`
- **When to Use**: Writing backend tests for Phase 1+
- **Example**: Testing JWT authentication, user registration

#### 2. **React Testing**

- **Location**: `.agents/skills/react-testing/SKILL.md`
- **Purpose**: Component, hook, and store testing patterns
- **Coverage**: Jest setup, React Testing Library queries, user interactions
- **Key Files**: `frontend/src/__tests__/`
- **When to Use**: Writing frontend component tests
- **Example**: Testing login form, protected routes

#### 3. **Database Design**

- **Location**: `.agents/skills/database-design/SKILL.md`
- **Purpose**: PostgreSQL schema design, normalization, Alembic migrations
- **Coverage**: Entity relationships, indexing, query optimization, constraints
- **Key Files**: `backend/app/db/models/`
- **When to Use**: Designing new data models or migrations
- **Example**: User authentication schema, order management entities

#### 4. **API Design**

- **Location**: `.agents/skills/api-design/SKILL.md`
- **Purpose**: REST API endpoint design, status codes, documentation
- **Coverage**: CRUD patterns, error handling, pagination, versioning
- **Key Files**: `backend/app/api/routes/`
- **When to Use**: Designing new API endpoints
- **Example**: Auth endpoints (`/register`, `/login`, `/refresh`)

---

## 📡 MCPs (Installed)

MCPs provide direct access to external systems and tools.

### 1. **PostgreSQL MCP**

- **Location**: `.agents/mcps/postgresql.md`
- **Purpose**: Direct database access for queries, schema inspection, migrations
- **Capabilities**:
  - List tables, columns, constraints, indexes
  - Execute SELECT queries
  - Verify migrations with Alembic
  - Performance analysis
- **Connection**: `postgresql://food_store_user:food_store_password@localhost:5432/food_store`
- **When to Use**:
  - Inspecting database schema
  - Verifying data after migrations
  - Analyzing query performance
  - Checking migration history
- **Example**: `SELECT * FROM users WHERE is_active = true;`

### 2. **GitHub MCP**

- **Location**: `.agents/mcps/github.md`
- **Purpose**: Repository management, issues, PRs, workflows
- **Capabilities**:
  - Create/list/close issues
  - Create/review/merge PRs
  - Check workflow status
  - Manage branches and commits
- **Repository**: `https://github.com/jjo1990/opencode-food-store`
- **When to Use**:
  - Creating issues from requirements
  - Opening PRs for code review
  - Checking CI/CD status
  - Linking issues to PRs
- **Example**: `gh pr create --title "feat(auth): JWT implementation"`

### 3. **Filesystem MCP**

- **Location**: `.agents/mcps/filesystem.md`
- **Purpose**: File search, directory analysis, bulk operations
- **Capabilities**:
  - Glob patterns for file discovery
  - Content search with regex
  - Directory structure analysis
  - File metrics
- **When to Use**:
  - Finding files by pattern
  - Searching for code patterns
  - Understanding project structure
  - Finding examples to follow
- **Example**: `find backend -name "*.py" -path "*/api/*"`

---

## 🔄 Skill Usage Workflow

### Phase 1: Authentication & Authorization

1. **Design Database Schema**
   - Load: `database-design` skill
   - Create: Users, refresh tokens, audit logs tables
   - Tools: Alembic migrations

2. **Design API Endpoints**
   - Load: `api-design` skill
   - Create: `/register`, `/login`, `/refresh`, `/logout`
   - Tools: FastAPI route handlers

3. **Implement Backend**
   - Use: `fastapi-testing` skill for tests
   - Create: Auth service, JWT token logic
   - Test: Registration, login, token refresh

4. **Implement Frontend**
   - Use: `react-testing` skill for tests
   - Create: LoginForm, ProtectedRoute components
   - Test: Form validation, API integration

5. **Verify & Deploy**
   - Use: `PostgreSQL MCP` to verify schema
   - Use: `GitHub MCP` to create PR
   - Use: `Filesystem MCP` to find configuration files

### Learning Path

1. **New to the project?** → Read `README.md` + `docs/`
2. **Need to design something?** → Load `database-design` or `api-design`
3. **Need to test?** → Load `fastapi-testing` or `react-testing`
4. **Need to explore code?** → Use `Filesystem MCP`
5. **Need to check state?** → Use `PostgreSQL MCP` or `GitHub MCP`

---

## 📋 Quick Reference

### Common Tasks & Skills

| Task                   | Skill           | MCP        |
| ---------------------- | --------------- | ---------- |
| Design user table      | database-design | PostgreSQL |
| Create login endpoint  | api-design      | -          |
| Test login form        | react-testing   | -          |
| Test login API         | fastapi-testing | -          |
| Find auth files        | -               | Filesystem |
| Check migration status | -               | PostgreSQL |
| Create PR for Phase 1  | -               | GitHub     |

### File Organization

```
food-store/
├── .agents/
│   ├── skills/
│   │   ├── fastapi-testing/      ← Backend testing patterns
│   │   ├── react-testing/        ← Frontend testing patterns
│   │   ├── database-design/      ← Schema design patterns
│   │   ├── api-design/           ← REST API patterns
│   │   └── find-skills/          ← Skill discovery
│   └── mcps/
│       ├── postgresql.md          ← Database queries
│       ├── github.md             ← PR/Issue management
│       └── filesystem.md         ← Code search
├── backend/
│   ├── app/
│   │   ├── api/routes/           ← API endpoints (use api-design)
│   │   ├── db/models/            ← Database models (use database-design)
│   │   └── services/             ← Business logic
│   └── tests/                    ← Tests (use fastapi-testing)
├── frontend/
│   ├── src/
│   │   ├── components/           ← React components
│   │   ├── hooks/                ← Custom hooks
│   │   └── store/                ← Zustand state
│   └── src/__tests__/            ← Tests (use react-testing)
└── docs/
    ├── Descripcion.txt           ← Vision & stack
    ├── Integrador.txt            ← Architecture & ERD
    └── Historias_de_usuario.txt  ← User stories & acceptance criteria
```

---

## 🚀 Phase 1: Authentication Checklist

### Design Phase

- [ ] Load `database-design` skill
- [ ] Design user, refresh_token, audit_log tables
- [ ] Use PostgreSQL MCP to verify schema

- [ ] Load `api-design` skill
- [ ] Design auth endpoints (/register, /login, /refresh, /logout)
- [ ] Define request/response schemas

### Implementation Phase

- [ ] Backend: Create models (use database-design)
- [ ] Backend: Create migrations (Alembic)
- [ ] Backend: Implement routes (use api-design)
- [ ] Backend: Add tests (use fastapi-testing)

- [ ] Frontend: Create forms (use react-testing)
- [ ] Frontend: Create hooks (useAuth)
- [ ] Frontend: Add tests (use react-testing)

### Verification Phase

- [ ] Use PostgreSQL MCP to check schema
- [ ] Use Filesystem MCP to find all auth files
- [ ] Use GitHub MCP to create Phase 1 PR
- [ ] All tests passing: `npm test` + `pytest backend/tests`

---

## 🔧 Installation & Updates

### Adding a New Skill

1. Create directory: `.agents/skills/<skill-name>/`
2. Create `SKILL.md` with patterns and examples
3. Update this registry with new skill info

Example:

```bash
mkdir -p .agents/skills/new-skill
touch .agents/skills/new-skill/SKILL.md
```

### Adding a New MCP

1. Create file: `.agents/mcps/<mcp-name>.md`
2. Document capabilities, authentication, examples
3. Update this registry with new MCP info

### Updating Registry

After adding skills/MCPs:

```bash
# This registry is the source of truth
# Update manually or use find-skills for discovery
```

---

## 📞 Support & Troubleshooting

### Can't Find a File?

Use **Filesystem MCP** with glob patterns:

```
find backend -name "*auth*"
find . -path "*/migrations/*"
```

### Need to Design a Table?

Load **Database Design** skill and follow the patterns:

```
- Normalize to 3NF
- Add timestamps
- Index foreign keys
- Use appropriate data types
```

### Need to Design an Endpoint?

Load **API Design** skill and follow conventions:

```
- Resource-based URLs
- Appropriate HTTP methods
- Document all status codes
- Follow error response format
```

### Need to Write Tests?

Load the appropriate testing skill:

```
- Backend: fastapi-testing
- Frontend: react-testing
```

---

## 📚 See Also

- `README.md` — Project overview and setup
- `docs/Descripcion.txt` — Vision and stack technology
- `docs/Integrador.txt` — Architecture and design patterns
- `docs/Historias_de_usuario.txt` — User stories and requirements
- `openspec/` — Specification documents and change artifacts
