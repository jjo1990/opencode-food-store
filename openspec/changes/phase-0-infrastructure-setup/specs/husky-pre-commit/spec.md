## Requisito: Husky Pre-commit Hooks

### Descripción

Pre-commit hooks que previenen pushear código que rompe lint, type checks o tests. Usando Husky + lint-staged para ejecutar validaciones solo en archivos modificados (rápido).

### Requisitos Funcionales

1. **Husky setup**:
   - `.husky/` folder con scripts de hooks
   - Instalación automática en `npm install` via husky postinstall
2. **Pre-commit hook** ejecuta:
   - `lint-staged` que corre linters solo en staged files
   - ESLint en `*.ts`, `*.tsx`, `*.js`
   - Ruff en `*.py`
   - Prettier autofix en `*.json`, `*.md`
3. **Pre-push hook** (opcional pero recomendado):
   - Ejecuta `npm run type-check` (validar tipos)
   - Ejecuta `npm run test` (validar tests antes de push)
   - Si falla, bloquea el push
4. **.lintstagedrc.json** declara reglas:
   ```json
   {
     "*.{ts,tsx}": ["eslint --fix"],
     "*.py": ["ruff check --fix"],
     "*.{json,md}": ["prettier --write"]
   }
   ```
5. **Bypass control**:
   - `git commit --no-verify` para saltarse hooks (documentado)
   - `git push --no-verify` para saltarse pre-push

### Requisitos No-Funcionales

1. Pre-commit hooks deben ejecutar en < 2 segundos (lint-staged solo staged files)
2. No debe haber false positives (hooks no bloquean código válido)
3. Hooks no deben modificar archivos más allá de lo necesario (solo autofix)
4. Setup debe ser automático en `npm install` (Husky postinstall)

### Criterio de Aceptación

- ✅ Crear archivo `.ts` con console.log, intentar commit → rechazado
- ✅ Crear archivo `.py` con línea muy larga, intentar commit → autofix con black
- ✅ Ejecutar `git commit --no-verify` → bypass funciona
- ✅ Pre-push hook bloquea si tests fallan
- ✅ New developer: `npm install` + `git commit` funciona sin configuración extra

### Referencias Técnicas

**Files creados/modificados:**
- `.husky/pre-commit` (script)
- `.husky/pre-push` (script)
- `.lintstagedrc.json` (configuration)
- `package.json` (postinstall script para husky)

**Estructura de hooks:**
```bash
# .husky/pre-commit
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

npx lint-staged
```

**Dependencias:**
- `husky`
- `lint-staged`

**Convenciones:**
- Hook files son executables (chmod +x)
- Scripts son shell scripts (bash/sh compatible)
- Errores en hooks detienen la operación (git commit o git push falla)
- Logs deben ser claros (mostrar qué falló)
