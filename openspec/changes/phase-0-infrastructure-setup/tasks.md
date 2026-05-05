## 1. Estructura de Monorepo con Turborepo

- [ ] 1.1 Instalar Turborepo globalmente: `npm install -g turbo`
- [ ] 1.2 Crear `turbo.json` en root con tasks de build, lint, test, dev
- [ ] 1.3 Crear `/packages` para código compartido (types, utils)
- [ ] 1.4 Configurar workspaces en `package.json` root (backend, frontend, packages/\*)
- [ ] 1.5 Verificar que `turbo run build` ejecuta builds de ambos workspaces

## 2. TypeScript Configuration

- [ ] 2.1 Crear `tsconfig.json` root base con strict mode habilitado
- [ ] 2.2 Extender tsconfig en frontend: `frontend/tsconfig.json` con `target: ES2020`, `module: ESNext`
- [ ] 2.3 Configurar `tsconfig.json` para backend Node.js (si aplica para type checking)
- [ ] 2.4 Crear `packages/types/tsconfig.json` para tipos compartidos API
- [ ] 2.5 Agregar script `npm run type-check` en root que valida todos los typescripts
- [ ] 2.6 Verificar que no hay `any` implícito: `noImplicitAny: true` en config

## 3. ESLint + Prettier Setup

- [ ] 3.1 Instalar `eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin` en frontend
- [ ] 3.2 Crear `.eslintrc.json` frontend con reglas React + TypeScript
- [ ] 3.3 Crear `.prettierrc.json` root (100 char line length, tabs: false, semi: true)
- [ ] 3.4 Crear `.prettierignore` (node_modules, dist, build, .next)
- [ ] 3.5 Agregar script `npm run lint` en frontend
- [ ] 3.6 Agregar script `npm run format` en root que ejecuta prettier --write en todo
- [ ] 3.7 Crear reglas custom para rechazar console.log en producción (dev tool)
- [ ] 3.8 Instalar ruff en backend y crear `pyproject.toml` con config ruff

## 4. Testing Framework Setup

**Frontend (Jest + React Testing Library)**

- [ ] 4.1 Instalar `jest @testing-library/react @testing-library/jest-dom ts-jest` en frontend
- [ ] 4.2 Crear `jest.config.js` con setup: TypeScript transpiling, moduleNameMapper para paths
- [ ] 4.3 Crear carpeta `frontend/src/__tests__/` como estructura base
- [ ] 4.4 Crear `frontend/src/__tests__/setup.ts` que importa @testing-library/jest-dom
- [ ] 4.5 Crear template de test: `frontend/src/__tests__/Example.test.tsx`
- [ ] 4.6 Agregar script `npm run test` en frontend
- [ ] 4.7 Agregar script `npm run test:watch` para desarrollo

**Backend (Pytest)**

- [ ] 4.8 Instalar `pytest pytest-cov pytest-asyncio` en backend
- [ ] 4.9 Crear `backend/pyproject.toml` con config pytest (testpaths, asyncio_mode)
- [ ] 4.10 Crear carpeta `backend/tests/` con estructura: unit/, integration/, conftest.py
- [ ] 4.11 Crear `backend/tests/conftest.py` con fixtures comunes (test_db, test_client, test_user)
- [ ] 4.12 Crear template de test: `backend/tests/unit/test_example.py`
- [ ] 4.13 Agregar script `pytest` en backend/pyproject.toml

## 5. Docker Setup

- [ ] 5.1 Crear `Dockerfile` en frontend con multi-stage (build + serve con nginx)
- [ ] 5.2 Crear `Dockerfile` en backend con Python 3.11 slim y pip caching
- [ ] 5.3 Crear `.dockerignore` root (node_modules, .git, .env)
- [ ] 5.4 Crear `docker-compose.yml` root con servicios: postgres, backend, frontend
- [ ] 5.5 Agregar `db-init.sql` para crear DB y usuario en postgres
- [ ] 5.6 Verificar que `docker-compose up` levanta todo sin errores
- [ ] 5.7 Crear `docker-compose.override.yml` para desarrollo (volúmenes, env vars extra)

## 6. GitHub Actions CI Pipeline

- [ ] 6.1 Crear `.github/workflows/ci.yml` con trigger en push a main + PRs
- [ ] 6.2 Job 1 - Lint: instala deps, corre `npm run lint` en frontend + ruff en backend
- [ ] 6.3 Job 2 - Type Check: corre `npm run type-check` en frontend
- [ ] 6.4 Job 3 - Tests: corre `npm run test` frontend + `pytest` backend (paralelo en 2 jobs)
- [ ] 6.5 Job 4 - Build: hace build de frontend + backend (solo si pasos anteriores pasaron)
- [ ] 6.6 Configurar cache de GitHub Actions: node_modules y pip packages
- [ ] 6.7 Agregar status check en rama main: CI debe pasar antes de merge
- [ ] 6.8 Testar workflow en una rama de feature: push y verificar que corre

## 7. Pre-commit Hooks con Husky

- [ ] 7.1 Instalar `husky` en root: `npm install husky --save-dev`
- [ ] 7.2 Ejecutar `npx husky install` para crear `.husky/` folder
- [ ] 7.3 Instalar `lint-staged` en root
- [ ] 7.4 Crear `.husky/pre-commit` que ejecuta lint-staged
- [ ] 7.5 Crear `.lintstagedrc.json` con reglas: `*.ts/*.tsx` → eslint, `*.py` → ruff
- [ ] 7.6 Crear `.husky/pre-push` que corre tests locales antes de push
- [ ] 7.7 Testar hooks: crear un commit con error intencional, verificar que se bloquea
- [ ] 7.8 Agregar instrucción a README: cómo saltarse con `--no-verify` si es necesario

## 8. Development Environment Documentation

- [ ] 8.1 Crear `DEV_SETUP.md` en root con pasos numerados
- [ ] 8.2 Documentar requisitos: Node 18+, Python 3.11+, Docker Desktop, Git
- [ ] 8.3 Agregar sección "First Time Setup": clone → `npm install` → `docker-compose up`
- [ ] 8.4 Crear troubleshooting section: "Docker no levanta", "Ports en uso", "DB connection error"
- [ ] 8.5 Documentar convenciones: naming (camelCase frontend, snake_case backend), commit messages
- [ ] 8.6 Agregar "Common Commands": `npm run dev`, `npm run test`, `npm run lint`, `docker-compose logs`
- [ ] 8.7 Crear diagrama ASCII de estructura monorepo
- [ ] 8.8 Documentar cómo agregar nuevo módulo (backend) o feature (frontend)

## 9. Integration + Verification

- [ ] 9.1 Crear rama de feature `phase-0-setup` y pushear a GitHub
- [ ] 9.2 Verificar que GitHub Actions corre sin errores
- [ ] 9.3 Crear PR y verificar que todos los checks pasan
- [ ] 9.4 Testar setup local completo: clonar en carpeta limpia, seguir DEV_SETUP.md paso a paso
- [ ] 9.5 Validar que `docker-compose up` levanta backend, frontend y postgres
- [ ] 9.6 Validar que `npm run test` pasa en ambos workspaces
- [ ] 9.7 Validar que `npm run lint` detecta error intencional y lo reporta
- [ ] 9.8 Mergear a main cuando todo pase

## Estimaciones de Esfuerzo

| Grupo           | Tareas   | Estimación | Bloqueantes            |
| --------------- | -------- | ---------- | ---------------------- |
| Monorepo        | 1.1-1.5  | 2h         | No                     |
| TypeScript      | 2.1-2.6  | 1.5h       | Monorepo               |
| ESLint/Prettier | 3.1-3.8  | 2h         | TypeScript             |
| Tests           | 4.1-4.13 | 3h         | ESLint                 |
| Docker          | 5.1-5.7  | 2.5h       | Tests (parallelizable) |
| GitHub Actions  | 6.1-6.8  | 2h         | Docker                 |
| Husky           | 7.1-7.8  | 1h         | Docker                 |
| Documentation   | 8.1-8.8  | 1.5h       | Todo anterior          |
| Verification    | 9.1-9.8  | 1.5h       | Todo anterior          |

**Total estimado: 17 horas concentradas, o 2-3 días con 1-2 developers**

## Success Criteria por Tarea

✅ **Grupo 1 (Monorepo):** `turbo run build` ejecuta sin error
✅ **Grupo 2 (TypeScript):** `npm run type-check` no reporta errores  
✅ **Grupo 3 (ESLint):** `npm run lint` ejecuta sin cambios en setup
✅ **Grupo 4 (Tests):** `npm run test` pasa al menos un test mock en ambos workspaces
✅ **Grupo 5 (Docker):** `docker-compose up` levanta 3 servicios correctamente
✅ **Grupo 6 (CI):** GitHub Actions workflow ejecuta todos los jobs en paralelo < 5 min
✅ **Grupo 7 (Husky):** Commit con cambio en .eslintrc es rechazado por pre-commit
✅ **Grupo 8 (Docs):** Nuevo dev sigue DEV_SETUP.md sin ayuda y logra clonar + levantar localmente
✅ **Grupo 9 (Verification):** PR puede ser mergeado sin fallos en CI
