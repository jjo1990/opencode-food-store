## Context

Food Store v5.0 será un e-commerce full-stack con 50+ cambios distribuidos a lo largo de 12-15 semanas. El equipo necesita moverse rápido pero sin sacrificar calidad. La principal fricción actual es que no hay un lugar centralizado de verdad para convenciones de desarrollo: cada developer estaría configurando su propio TypeScript, sus tests, su ambiente de desarrollo.

**Restricciones del contexto:**

- Stack ya definido: React + FastAPI, TypeScript en frontend, Python en backend
- Equipo pequeño (probablemente < 5 developers) donde la comunicación de convenciones tiene que ser explícita
- Monorepo necesario para compartir tipos (API contracts) y herramientas
- CI/CD debe ser rápido (tests < 5 min) para no frustrar a developers

## Goals / Non-Goals

**Goals:**

- Establecer estructura monorepo consistente que acelere el desarrollo sin crear complejidad
- Automatizar calidad: linting, tipos, tests en pre-commit y CI
- Hacer que setup de entorno sea reproducible y sin fricción (docker-compose)
- Crear templates de tests que todos sigan, reduciendo bike-shedding
- Documentar convenciones de forma que sean fáciles de buscar y entender

**Non-Goals:**

- No estamos arreglando el stack tecnológico (React, FastAPI, PostgreSQL ya están decididos)
- No estamos haciendo deployment a producción (eso es Phase 1+)
- No estamos configurando secrets/vaults avanzados (básico con .env.example es suficiente por ahora)
- No estamos optimizando bundle size aún (eso se hace después de tener features)

## Decisions

### 1. Monorepo: Turborepo vs Nx

**Decisión:** Turborepo

**Rationale:**

- Turborepo es **más liviano** que Nx: menos boilerplate, curva de aprendizaje menor
- Config mínima (turbo.json) vs Nx que requiere angular.json complejo
- Perfecto para equipos pequeños que necesitan coordinar 2-3 workspaces (backend, frontend, shared)
- **Remote caching**: si conectamos a Vercel, los builds son más rápidos en CI

**Alternativas consideradas:**

- **Pnpm workspaces**: Muy bajo nivel, requeriría escribir mucha orchestración a mano
- **Nx**: Más potente pero overhead innecesario para nuestro tamaño

### 2. Testing: Jest + Vitest para Frontend, Pytest para Backend

**Decisión:**

- Frontend: Jest (porque ya está en el ecosistema React)
- Backend: Pytest (estándar Python)

**Rationale:**

- Jest tiene soporte nativo para React Testing Library y snapshots
- Vitest sería alternativa más rápida, pero Jest es más maduro y conocido
- Pytest es el estándar Python; todos los devs de FastAPI lo conocen
- Ambos tienen buen soporte para coverage y CI integration

**Alternativas consideradas:**

- **Vitest everywhere**: Demasiado experimental para un proyecto que va a estar en producción
- **Mocha/Chai**: Viejo, requiere más setup manual

### 3. Linting: ESLint + Prettier (frontend), Ruff (backend)

**Decisión:**

- Frontend: ESLint + Prettier (config strict para TypeScript)
- Backend: Ruff (linter Python muy rápido, escrito en Rust)

**Rationale:**

- ESLint + Prettier: combo estándar, autofix en pre-commit
- Ruff es 10-100x más rápido que Flake8/Pylint
- Pre-commit hooks pueden fallar si no son rápidos — Ruff nunca es cuello de botella

**Alternativas consideradas:**

- **Pylint**: Bueno pero lento; Ruff lo reemplaza completamente
- **StandardJS**: Menos flexible que ESLint; queremos control sobre reglas

### 4. Docker: docker-compose para dev, multi-stage Dockerfile para prod

**Decisión:**

- Usar docker-compose.yml para desarrollo local (backend + frontend + postgres)
- Dockerfile multi-stage para build en CI
- .dockerignore para excluir node_modules, .git, etc.

**Rationale:**

- docker-compose = setup reproducible, sin "funciona en mi máquina"
- Multi-stage build = imagen final pequeña, sin dev dependencies
- Una sola versión de Postgres para todos (evita incompatibilidades SQLite vs Postgres)

**Alternativas consideradas:**

- **Makefile**: Funciona pero docker es más portable entre SOs
- **Bash scripts**: Mismo problema

### 5. CI/CD: GitHub Actions

**Decisión:** GitHub Actions (está integrado en GitHub, sin costo extra)

**Rationale:**

- Ya estamos en GitHub, no hay que ir a otro servicio
- YAML simple y versionado en el repo
- Caché integrado para node_modules y pip packages
- Jobs en paralelo = tests rápidos

**Flujo:**

```
PR push → lint → type check → test → build → bloquea merge si falla
```

**Alternativas consideradas:**

- **CircleCI**: Bueno pero pago; GitHub Actions es suficiente
- **Travis CI**: Abandonado

### 6. Pre-commit: Husky + lint-staged

**Decisión:** Husky para hooks, lint-staged para correr linters solo en staged files

**Rationale:**

- Husky es simple: una carpeta .husky/ con scripts
- lint-staged previene que commitees código que no passa lint
- Hooks rápidos = developers no se frustran (< 2 segundos)
- Fácil de saltarse si es necesario (`git commit --no-verify`)

**Alternativas consideradas:**

- **Git hooks manuales**: Frágiles, difíciles de compartir
- **Pre-push**: Menos útil porque fallos se descubren demasiado tarde

## Risks / Trade-offs

| Risk                                            | Mitigación                                                                           |
| ----------------------------------------------- | ------------------------------------------------------------------------------------ |
| Monorepo crece y se vuelve lento                | Remoto caching de Turborepo; separar responsablemente en la futura                   |
| Developers no respetan pre-commit (--no-verify) | Documentación; CI lo bloquea igual. No hay forma de forzar si alguien es testarudo   |
| Tests lentos ralentizan CI                      | Usar flag `--maxWorkers=2` en CI para no saturar; paralelizar jobs de GitHub Actions |
| Docker en Windows es lento                      | WSL2 reduce el overhead mucho; documentar en dev guide                               |
| TypeScript strict mode es muy restrictivo       | Empezamos strict, podemos relajar. Mejor empezar fuerte y soltar que lo inverso      |

## Migration Plan

Esto es Phase 0 = nada que migrar. Pero sí tenemos que planear cómo se van a usar estos cimientos en Phase 1+:

**Phase 1+ (otros cambios):**

- Cada nuevo feature va en una carpeta feature-first dentro de backend/app/modules/ o frontend/src/features/
- New tests siempre siguen los templates establecidos aquí
- Pull requests DEBEN tener pruebas verificadas en CI antes de merge
- Si alguien necesita deshabilitar un linter rule, lo documenta en el PR con el motivo

## Open Questions

1. ¿Vamos a usar Postgres en desarrollo local o SQLite para mayor velocidad? → Decidimos: Postgres en docker-compose para parity con prod
2. ¿Qué cobertura mínima de tests vamos a exigir? → Pendiente definir (sugerencia: 70%+ en módulos nuevos)
3. ¿Secrets (tokens, DB_PASSWORD) en GitHub? → Usar .env.example (sin valores) + GitHub Secrets para CI
