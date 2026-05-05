## Requisito: Configuración TypeScript Strict

### Descripción

TypeScript debe estar configurado en strict mode en toda la aplicación. Esto significa que el compilador rechaza patrones inseguros (implícitos `any`, null checks missing, etc.) forzando que el código sea type-safe desde el inicio. Reduce bugs en producción significativamente.

### Requisitos Funcionales

1. **tsconfig.json root** con `strict: true` y `noImplicitAny: true`
2. **Frontend tsconfig.json** extiende root:
   - `target: ES2020` (moderno, soportado en navegadores recientes)
   - `module: ESNext` (importa/exports nativos)
   - `jsx: react-jsx` (React 17+ jsx transform)
   - `moduleResolution: bundler` (Vite resolver)
3. **Backend tsconfig.json** (si aplica):
   - `target: ES2020` (Node 18+)
   - `module: commonjs` o `ESNext` según setup
4. **Path aliases** deben funcionar: `@/components`, `@/utils`
5. **type-check script** valida ambos workspaces sin errores

### Requisitos No-Funcionales

1. Type checking debe ser < 10s en ambos workspaces
2. IDE autocomplete debe funcionar (VSCode Intellisense)
3. Build debe fallar si hay errores de tipo
4. No debe haber `// @ts-ignore` o `any` explícito sin justificación

### Criterio de Aceptación

- ✅ `npm run type-check` pasa sin errores
- ✅ `// @ts-expect-error` es usado para errores intencionales (documentados)
- ✅ `tsc --noEmit` valida sin cambios en archivos
- ✅ VSCode muestra errores de tipo en tiempo real
- ✅ Ningún `any` implícito es permitido (test: cambiar a `any` debería fallar check)

### Referencias Técnicas

**Files creados/modificados:**
- `tsconfig.json` (root)
- `frontend/tsconfig.json` (extends root)
- `backend/tsconfig.json` (si aplica)
- `tsconfig.build.json` (optional, para build vs editor)

**Dependencias:**
- `typescript` (ya en proyecto)

**Convenciones:**
- Type definitions van en `types/` folder (ej: `types/api.ts`, `types/models.ts`)
- Interfaces públicas se exportan desde `index.ts` en cada module
- No se usan `type` vs `interface` sin razón (consistencia)

### Notas de Implementación

- Si código existente tiene errores de tipo, fase 0 establece la baseline; fase 1+ los limpia
- `skipLibCheck: true` reduce check time si librerías tienen errores (pero es workaround)
