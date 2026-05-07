# GitHub MCP

**Model Context Protocol for GitHub Repository Management**

## Overview

This MCP provides direct access to GitHub for managing issues, pull requests, commits, and repository metadata.

## Features

- **Issue Management**: Create, list, update, close issues
- **Pull Request Operations**: Create, review, merge PRs
- **Repository Data**: Branches, commits, tags, releases
- **Workflow Integration**: Check runs, actions, status

## Configuration

### Environment Variables

```env
GITHUB_TOKEN=<your-personal-access-token>
GITHUB_REPO=jjo1990/opencode-food-store
GITHUB_OWNER=jjo1990
```

### Access Token Setup

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate new token with scopes:
   - `repo` (full control)
   - `workflow` (actions)
   - `read:org` (read organization)

## Common Operations

### Issue Management

```bash
# List open issues
gh issue list --state open

# Create issue
gh issue create --title "Title" --body "Description" --label "bug"

# List issues by label
gh issue list --label "Phase-1" --state open

# Close issue
gh issue close <issue-number>
```

### Pull Request Operations

```bash
# List open PRs
gh pr list --state open

# Create PR
gh pr create --title "Title" --body "Description" --base main

# View PR details
gh pr view <pr-number>

# Check PR status
gh pr status

# Merge PR
gh pr merge <pr-number> --merge
```

### Repository Data

```bash
# List branches
gh repo list

# View commit history
git log --oneline -20

# Check current branch
git branch --show-current

# View tags
gh release list
```

## Integration with Food Store

### Issue Workflow

1. **Create Issue** → User story or bug report
2. **Label with Phase** → `Phase-0`, `Phase-1`, etc.
3. **Create Branch** → `git checkout -b feature/us-001-auth`
4. **Open PR** → Link to issue
5. **Merge & Close** → Issue auto-closes with PR merge

### Naming Conventions

**Branches**:
```
feature/us-001-auth
fix/us-001-password-reset
refactor/consolidate-structure
docs/authentication-guide
```

**Issues**:
```
[Phase-1] US-001: Authentication & Authorization
[Bug] Login fails with special characters
[Feature] Add two-factor authentication
```

**PRs**:
```
feat(auth): implement JWT authentication for user login
fix(auth): handle password reset edge case
refactor(db): consolidate backend/frontend structure
docs(auth): add authentication flow diagram
```

## Common Workflows

### Creating a Feature from Issue

```bash
# 1. Create issue on GitHub
gh issue create --title "US-001: Authentication" --label "Phase-1"

# 2. Create branch from issue
git checkout -b feature/us-001-auth

# 3. Make changes and commit
git add .
git commit -m "feat(auth): implement JWT authentication"

# 4. Push and create PR
git push -u origin feature/us-001-auth
gh pr create --title "feat(auth): implement JWT authentication" --body "Closes #<issue-number>"

# 5. Merge when ready
gh pr merge --merge
```

### Linking Issues and PRs

In PR description or commit message:
```
Closes #123
Fixes #456
Related to #789
```

## Integration Points

### With OPSX Workflow

Each OPSX change should have:
- [ ] GitHub Issue created (specification)
- [ ] Branch created from issue
- [ ] PR created linking to issue
- [ ] PR merged and issue closed

Example PR for Phase 1:

```markdown
## Phase 1: Authentication & Authorization

Closes #<issue-number>

### Changes
- Implement JWT authentication
- Add RBAC system
- Implement refresh token rotation

### Design
See `openspec/changes/phase-1-auth/design.md`

### Tests
- [ ] Unit tests: 95%+ coverage
- [ ] Integration tests: JWT flow
- [ ] E2E tests: Login/logout

### Checklist
- [ ] Design reviewed
- [ ] All tests passing
- [ ] Documentation updated
```

## When to Use This MCP

- ✅ Creating and updating issues
- ✅ Managing PRs and reviews
- ✅ Checking CI/CD status
- ✅ Listing branches and releases
- ✅ Automating workflows
- ❌ Don't use for: Direct repository cloning (use git instead)

## See Also

- `README.md` — Contribution guidelines
- `.github/workflows/` — CI/CD pipeline definitions
- `docs/` — Architecture and design documents
