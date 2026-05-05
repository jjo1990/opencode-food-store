## Why

Food Store v5.0 va a ser un e-commerce completo. Pero antes de escribir una línea de código de funcionalidad, necesitamos armar los **cimientos** sobre los que todo va a vivir. Sin Phase 0, cada developer va a estar reinventando la rueda: configurando TypeScript a mano, escribiendo tests de forma inconsistente, haciendo deploys manuales.

**Por qué ahora?** Porque este es el momento de definir las convenciones una sola vez y que 50 cambios futuros se construyan sobre bases sólidas y consistentes.

## What Changes

Phase 0 establece la infraestructura compartida que habilita el desarrollo efectivo del resto del sistema:

- **Monorepo setup**: Estructura unificada con Turborepo para coordinar backend (FastAPI), frontend (React) y compartir herramientas
- **Build tooling**: TypeScript configurado con strict mode, ESLint con reglas coherentes, Prettier para formato automático
- **CI/CD pipeline**: GitHub Actions que corre tests, lint y build automáticamente en cada push
- **Docker containerization**: Imágenes para backend, frontend y PostgreSQL; docker-compose para dev local
- **Testing framework**: Jest para frontend, Pytest para backend; templates y convenciones establecidas
- **Pre-commit hooks**: Husky para prevenir commits que rompan lint o tests
- **Development environment docs**: Guía paso a paso para que un nuevo dev clone y esté corriendo en 10 minutos

## Capabilities

### New Capabilities

- `monorepo-structure`: Estructura compartida con Turborepo que permite coordinar backend, frontend y herramientas comunes con coherencia
- `typescript-configuration`: Configuración strict de TypeScript en frontend con type checking máximo en pre-commit
- `eslint-prettier-setup`: Linting automático y formato consistente en todo el monorepo
- `github-actions-ci`: Pipeline de CI que valida tests, lint y builds en cada pull request
- `docker-setup`: Containerización completa: backend, frontend y PostgreSQL con docker-compose para dev local
- `jest-vitest-testing`: Framework y templates para tests unitarios e integración (Jest en frontend, Pytest en backend)
- `husky-pre-commit`: Hooks pre-commit que previenen pushes que rompan la calidad
- `dev-environment-guide`: Documentación completa y automatización para setup inicial del entorno

### Modified Capabilities

(Ninguna — es Phase 0, no modificamos capacidades existentes)

## Impact

**Código afectado:**

- Toda la estructura de directorios del monorepo (backend/, frontend/, tools/)
- Configuración root: tsconfig.json, eslintrc, prettier.json, turbo.json
- CI/CD: .github/workflows/

**APIs públicas:**

- Endpoints y componentes heredarán las convenciones de TypeScript y linting establecidas aquí
- Tests de todos los módulos futuros seguirán los templates y patrones definidos en Phase 0

**Dependencias:**

- Turborepo, TypeScript, ESLint, Prettier, Jest, Vitest, Pytest, Husky, Docker
- Será la base sobre la que se asientan 50 cambios futuros

**Criterio de éxito:**

- ✅ Developer nuevo puede clonar, hacer `docker-compose up` y tener backend + frontend corriendo localmente
- ✅ `npm run lint` y `npm run test` pasan en todo el monorepo
- ✅ GitHub Actions corre automáticamente en cada PR y bloquea merge si hay errores
- ✅ Pre-commit hooks previenen commits rotos
- ✅ Documentación dev es clara y completa
