## Requisito: Estructura de Monorepo con Turborepo

### Descripción

La aplicación Food Store v5.0 necesita coordinar múltiples workspaces (backend FastAPI, frontend React, y código compartido) desde un único repositorio. Turborepo proporciona la orquestación necesaria para ejecutar builds, tests y linting de forma paralela y eficiente, mientras mantiene caching inteligente.

### Requisitos Funcionales

1. **Root package.json** debe definir workspaces que apunten a `backend/`, `frontend/` y `packages/*`
2. **turbo.json** debe declarar tasks globales:
   - `build`: compila frontend y backend
   - `dev`: levanta dev servers en paralelo
   - `test`: ejecuta tests en ambos workspaces
   - `lint`: valida código en ambos workspaces
3. **Remote caching** debe configurarse (conectando a Vercel o local)
4. **Output locations** deben estar mapeadas: `frontend/dist`, `backend/build`, etc.
5. **Dependencies between tasks** deben estar declaradas (ej: build depende de type-check)

### Requisitos No-Funcionales

1. Setup debe tomar < 5 minutos (npm install + turbo caching)
2. Turbo run commands no deben imprimir noise innecesario (usar `--concurrency=4`)
3. CI pipeline debe reutilizar caché de builds anteriores (ahorrar 3+ minutos por CI run)
4. Estructura debe permitir agregar nuevos workspaces sin modificar root config (pattern-based)

### Criterio de Aceptación

- ✅ `turbo run build` compila frontend y backend sin errores
- ✅ `turbo run dev` levanta ambos dev servers en paralelo
- ✅ `turbo run lint` valida código en ambos workspaces
- ✅ `turbo run test` ejecuta tests en paralelo
- ✅ Caché de Turborepo reduce segundo run en 70%+ (observable con `turbo run build --verbose`)
- ✅ Nuevo workspace puede agregarse en 2 pasos: carpeta + línea en package.json

### Referencias Técnicas

**Files creados/modificados:**
- `package.json` (root) — workspaces
- `turbo.json` (root) — task definitions
- `backend/package.json` — scripts de backend
- `frontend/package.json` — scripts de frontend

**Dependencias agregadas:**
- `turbo` (npm global o local)
- Backend y frontend mantienen sus dependencies independientes

**Convenciones:**
- Todos los scripts en package.json siguen pattern: `npm run <task>`
- Output directories: `{workspace}/dist` o `{workspace}/build`
- Task names son siempre lowercase, hyphenated (ej: `type-check`, no `typeCheck`)
