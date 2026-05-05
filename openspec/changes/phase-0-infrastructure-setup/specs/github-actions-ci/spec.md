## Requisito: GitHub Actions CI Pipeline

### Descripción

Automatizar validación en cada push y PR: linting, type checking, tests y builds deben ejecutarse en paralelo en GitHub Actions. Esto previene que código roto sea mergeado a main.

### Requisitos Funcionales

1. **Workflow file** en `.github/workflows/ci.yml`:
   - Trigger: `on: [push, pull_request]` en todas las branches
   - Node.js setup: v18+
   - Python setup: 3.11+ (si aplica backend)
2. **Jobs ejecutados en paralelo** (3-5 min total):
   - Job 1: Lint (ESLint frontend + Ruff backend)
   - Job 2: Type Check (TypeScript compilation)
   - Job 3: Tests (Jest + Pytest)
   - Job 4: Build (producción builds)
3. **Caché integrado**:
   - `node_modules` debe ser cacheado (key basado en hash de package-lock.json)
   - pip packages deben ser cacheados (key basado en hash de requirements.txt)
4. **Status checks** configurados en branch main:
   - Merge bloqueado si algún job falla
5. **Notifications** en PR:
   - Status de CI visible en PR (pasando/fallando)
   - Detalles de error clickeables a GitHub Actions UI

### Requisitos No-Funcionales

1. CI pipeline debe completar en < 5 minutos (exitoso)
2. Fallos deben tomar < 10 segundos en detectarse (fail-fast)
3. Caché debe ahorrar 60%+ de tiempo en segundo run
4. Workflow debe soportar múltiples branches sin cambios
5. Log output debe ser legible (sin spam)

### Criterio de Aceptación

- ✅ Crear PR con cambio válido: todos los jobs pasan
- ✅ Crear PR con lint error: Lint job falla y muestra error específico
- ✅ Crear PR con test failure: Tests job falla y muestra qué test falló
- ✅ Merge a main es bloqueado si CI no pasa
- ✅ Caché de GitHub Actions es efectivo (segundo run es 60%+ rápido)

### Referencias Técnicas

**Files creados/modificados:**

- `.github/workflows/ci.yml`
- Branch protection rules en GitHub (Settings)

**Estructura básica:**

```yaml
name: CI

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: npm
      - run: npm install
      - run: npm run lint

  type-check:
    runs-on: ubuntu-latest
    # ... similar setup
    - run: npm run type-check

  test:
    runs-on: ubuntu-latest
    # ... setup
    - run: npm run test

  build:
    runs-on: ubuntu-latest
    needs: [lint, type-check, test]  # solo corre si los anteriores pasan
    # ... setup
    - run: npm run build
```

**Convenciones:**

- Jobs nombrados en lowercase-with-hyphens
- `runs-on: ubuntu-latest` para consistencia
- `timeout-minutes: 10` por si acaso
- Secrets (tokens, DB URLs) solo en variables de entorno definidas en GitHub Secrets
