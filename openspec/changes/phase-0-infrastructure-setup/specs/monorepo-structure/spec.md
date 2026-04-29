## ADDED Requirements

### Requirement: Monorepo workspace structure
The system SHALL organize code into a monorepo with clearly separated frontend applications, backend services, and shared packages using npm workspaces.

#### Scenario: Root package.json declares workspaces
- **WHEN** developer installs dependencies at project root
- **THEN** npm installs dependencies for all packages in `apps/`, `services/`, and `packages/` directories

#### Scenario: Frontend app exists in apps directory
- **WHEN** developer runs `npm run dev` from project root
- **THEN** frontend application in `apps/web` starts development server

#### Scenario: Backend service exists in services directory
- **WHEN** developer navigates to `services/api`
- **THEN** they find a complete Node.js/TypeScript service with its own package.json and build configuration

### Requirement: Shared code organization
The system SHALL provide a `packages/` directory for shared utilities, types, and components used across services and applications.

#### Scenario: Shared types package exists
- **WHEN** backend service and frontend app need to import common types
- **THEN** they import from `@food-store/types` package without duplication

#### Scenario: Shared utilities package exists
- **WHEN** multiple services need common helper functions
- **THEN** they import from `@food-store/utils` package

### Requirement: Clear directory boundaries
The system SHALL establish clear separation between frontend, backend, and shared code with no circular dependencies.

#### Scenario: Frontend cannot import backend code
- **WHEN** linting runs on the project
- **THEN** no import statements from `services/` are found in `apps/` directories

#### Scenario: Backend services are independent
- **WHEN** developing `services/auth` and `services/products`
- **THEN** neither service imports directly from the other; they communicate via REST API or message queue

### Requirement: Root-level configuration
The system SHALL provide configuration files at the monorepo root for tooling that spans all packages (TypeScript, ESLint, Prettier, Jest).

#### Scenario: TypeScript configuration inheritance
- **WHEN** a package extends tsconfig.json from root
- **THEN** it inherits common TypeScript settings and can override specific settings

#### Scenario: ESLint configuration inheritance
- **WHEN** a package extends .eslintrc from root
- **THEN** all packages follow the same linting rules
