## Requisito: ESLint + Prettier Setup

### Descripción

Linting y formato automático de código. ESLint valida que el código siga convenciones (sin console.log en prod, imports ordenados, etc.). Prettier formatea de forma consistente (indentation, línea breaks, semicolons). Juntos evitan bike-shedding y garantizan consistencia.

### Requisitos Funcionales

1. **Frontend ESLint** con plugins:
   - `@typescript-eslint` para reglas TypeScript
   - `eslint-plugin-react` para reglas React
   - `eslint-plugin-react-hooks` para validar hooks
2. **ESLint rules** deben:
   - Rechazar `console.log` en build (pero permitir en development)
   - Rechazar imports ciclícas (circular dependency)
   - Validar uso correcto de hooks (dependencies array)
   - Ordenar imports alfabéticamente
3. **Prettier config** debe tener:
   - Line length: 100 caracteres
   - Semicolons: true
   - Quotes: single (')
   - Tabs: false (spaces)
   - Trailing comma: es5
4. **lint script** ejecuta sin errors en clean code
5. **format script** puede autofix problemas comunes

### Requisitos No-Funcionales

1. Linting debe ser < 3s en ambos workspaces
2. Autofix (`eslint --fix`) debe resolver 90% de errores
3. Format script (`prettier --write`) debe ser idempotente
4. Conflictos eslint-prettier deben estar resueltos (usar `eslint-config-prettier`)

### Criterio de Aceptación

- ✅ `npm run lint` pasa sin errores en código limpio
- ✅ `npm run format` puede ejecutarse varias veces sin cambios en segundo run
- ✅ `eslint --fix` resuelve errores simples (imports, spacing)
- ✅ Editor (VSCode) muestra errores de linting en tiempo real
- ✅ Conflictos ESLint ↔ Prettier están resueltos

### Referencias Técnicas

**Files creados/modificados:**

- `.eslintrc.json` (frontend)
- `.prettierrc.json` (root, compartido)
- `.prettierignore`
- `.eslintignore`

**Dependencias (frontend):**

- `eslint`
- `@typescript-eslint/eslint-plugin`
- `@typescript-eslint/parser`
- `eslint-plugin-react`
- `eslint-plugin-react-hooks`
- `eslint-config-prettier`
- `prettier`

**Dependencias (backend):**

- `ruff` (Python linter, instalado via pip)

**Convenciones:**

- ESLint rules: `error` para críticos, `warn` para sugerencias
- Prettier config es compartida entre frontend/backend (mismo estilo)
- `.eslintignore` excluye: `node_modules/`, `dist/`, `build/`, `.next/`
