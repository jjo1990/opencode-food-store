## Context

Food Store v5.0 is a full-stack e-commerce platform with 77 user stories spanning customer, vendor, and admin capabilities. The project is currently empty (scaffold stage). We need to establish monorepo structure, build tooling, and CI/CD before any feature development. The team will use TypeScript, React/Next.js for frontend, Node.js for backend services, and PostgreSQL for data storage.

## Goals / Non-Goals

**Goals:**
- Establish a scalable monorepo structure (packages, apps, services)
- Configure build tooling (Next.js for frontend, Node.js/TypeScript for backend)
- Set up local development environment with proper configuration management
- Implement CI/CD pipelines (GitHub Actions) for automated testing and deployment
- Ensure code quality through linting, formatting, and pre-commit hooks
- Create reusable testing infrastructure (Jest, test utilities)
- Enable team members to bootstrap dev environment and start feature work

**Non-Goals:**
- Implement actual API endpoints or database migrations (done in later phases)
- Deploy to production (CI/CD pipeline setup only, actual deployment in later phase)
- Configure cloud infrastructure (AWS/GCP/etc) - that's a separate phase
- Create detailed coding standards documentation (will evolve organically)

## Decisions

### 1. Monorepo Pattern: npm workspaces (over Lerna, Turborepo)
**Rationale**: npm workspaces are built into Node.js toolchain, zero external dependencies, sufficient for Food Store's scope. Lerna adds complexity we don't need yet; Turborepo is overkill for current size.

**Trade-off**: Workspace management is simpler, but build orchestration requires custom scripts. If we scale to 20+ packages, we'd revisit.

### 2. Frontend Framework: Next.js 14+ (App Router)
**Rationale**: Next.js provides SSR, API routes, built-in optimization, and strong TypeScript support. App Router is the future standard.

**Trade-off**: Couples API layer to frontend (can separate later if needed). Learning curve for new team members.

### 3. Backend Structure: Feature-driven services in `/services`
**Rationale**: Each major domain (auth, products, orders, payments) gets its own service package. Shared code goes to `packages/`. This enables independent scaling and team ownership.

**Trade-off**: More packages to manage, but clear boundaries for feature ownership.

### 4. Testing: Jest + testing-library
**Rationale**: Jest is the industry standard for Node.js projects. testing-library encourages testing from user perspective. Both have excellent TypeScript support.

**Trade-off**: Requires test setup for each package, but yields better coverage discipline.

### 5. CI/CD: GitHub Actions (not external CI service)
**Rationale**: Integrated with GitHub, no vendor lock-in, sufficient for current scale. Runs on PRs, main branch, and tag-based releases.

**Trade-off**: Workflow files live in repo (version controlled ✓), but GitHub Actions YAML can be verbose.

### 6. Environment Management: `.env.local` files + process.env validation
**Rationale**: Simple, no external config service needed at this stage. Validation happens at app startup to catch config issues early.

**Trade-off**: Not suitable for secrets in production (will use secrets manager in deployment phase).

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Monorepo complexity grows with scale | Establish clear package boundaries and ownership from day 1; document workspace structure |
| Dependency conflicts across packages | Lock npm versions, regular audit runs, shared dependencies in root `package.json` |
| CI/CD pipeline bottleneck | Set up parallel job execution in GitHub Actions; cache dependencies aggressively |
| Dev environment setup takes too long | Create setup script (`npm run setup:dev`), document in README, use Docker Compose if needed later |
| TypeScript compilation time increases | Configure incremental builds, split build tasks across CI jobs |

## Migration Plan

**Phase 0 (this change):**
1. Create directory structure: `/services`, `/apps`, `/packages`
2. Set up root `package.json` with workspaces declaration
3. Initialize frontend with `create-next-app` in `apps/web`
4. Create backend service scaffold in `services/api`
5. Configure TypeScript, ESLint, Prettier, Jest at root and package level
6. Add GitHub Actions workflows for CI/CD
7. Create `.env.example` templates

**Follow-up Phases:**
- Phase 1: Set up database schema and migrations
- Phase 2: Implement auth service and core API
- Phase 3: Start feature development

**Rollback:**
Not applicable for infrastructure phase. If structure becomes problematic, we refactor in-place during Phase 1+.

## Open Questions

1. Should we use Docker for local development or native Node.js? (Defer to Phase 1 if complexity arises)
2. Which cloud provider for production deployment? (AWS assumed, but not finalized)
3. What's the approval flow for adding new packages to monorepo? (Document in contribution guidelines)
