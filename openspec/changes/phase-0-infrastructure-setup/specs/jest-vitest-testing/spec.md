## Requisito: Jest + Vitest Testing Framework

### Descripción

Setup de framework de testing para frontend (Jest) y backend (Pytest). Esto incluye templates de tests, fixtures comunes, y configuración para que sea fácil escribir tests de calidad desde el inicio.

### Requisitos Funcionales

**Frontend (Jest + React Testing Library)**

1. **jest.config.js** configura:
   - TypeScript transpiling via `ts-jest`
   - Module name mapper para path aliases (`@/components` → `src/components`)
   - Setup files para `@testing-library/jest-dom`
   - Test environment: `jsdom` para DOM testing
2. **Templates de test**:
   - Component test: `Component.test.tsx` testing render + user interactions
   - Hook test: `useCustomHook.test.ts` usando `@testing-library/react`
   - Utility test: `utils.test.ts` para funciones puras
3. **Test structure**:
   - Tests viven junto al código (`src/__tests__/` o `*.test.tsx` co-located)
   - Fixtures en `src/__tests__/fixtures/`
   - Mocks en `src/__tests__/mocks/`
4. **npm run test** targets:
   - `npm run test` — run once, coverage report
   - `npm run test:watch` — watch mode para desarrollo
   - `npm run test:coverage` — detailed coverage report

**Backend (Pytest)**

1. **pyproject.toml** configura pytest:
   - `testpaths: ["tests"]`
   - `asyncio_mode: auto` para FastAPI async tests
   - `python_files: ["test_*.py"]`
2. **conftest.py** proporciona fixtures:
   - `test_db`: instancia de base de datos limpia por test
   - `test_client`: cliente HTTP FastAPI TestClient
   - `test_user`: usuario de prueba con tokens
3. **Templates de test**:
   - Unit test: `tests/unit/test_utils.py`
   - Integration test: `tests/integration/test_endpoints.py`
   - Fixture-based: `tests/conftest.py`
4. **pytest targets**:
   - `pytest` — run all tests
   - `pytest -v` — verbose output
   - `pytest --cov` — coverage report

### Requisitos No-Funcionales

1. Tests deben ser independientes (no orden-dependientes)
2. Tests deben ser rápidos: frontend < 5s, backend < 10s para suite completo
3. Coverage debe ser trackable (generate reports)
4. Mocking debe ser fácil (factories, fixtures)
5. Async tests (backend) deben funcionar sin configuración manual

### Criterio de Aceptación

- ✅ `npm run test` pasa con al menos un test mock en frontend
- ✅ `pytest` pasa con al menos un test mock en backend
- ✅ `npm run test:coverage` genera reporte HTML legible
- ✅ `pytest --cov` genera reporte de cobertura
- ✅ Tests pueden usar path aliases sin problemas (`from @/utils`)
- ✅ Async tests (backend) no tienen warnings
- ✅ Fixtures (database, client, user) se usan correctamente

### Referencias Técnicas

**Files creados/modificados (Frontend):**
- `frontend/jest.config.js`
- `frontend/src/__tests__/setup.ts`
- `frontend/src/__tests__/Example.test.tsx` (template)
- `frontend/src/__tests__/fixtures/` (test data)
- `frontend/src/__tests__/mocks/` (mock functions)

**Files creados/modificados (Backend):**
- `backend/pyproject.toml` (pytest config)
- `backend/tests/conftest.py` (fixtures)
- `backend/tests/unit/test_example.py` (template)
- `backend/tests/integration/test_api.py` (template)

**Dependencias (Frontend):**
- `jest`
- `@testing-library/react`
- `@testing-library/jest-dom`
- `@testing-library/user-event`
- `ts-jest`
- `jest-environment-jsdom`

**Dependencias (Backend):**
- `pytest`
- `pytest-asyncio`
- `pytest-cov`
- `httpx` (async HTTP client para tests)

**Convenciones:**
- Test files: `*.test.ts`, `*.test.tsx` (frontend), `test_*.py` (backend)
- Fixtures: reutilizables, nombradas descriptivamente
- Mocks: NO usar snapshots para API responses (demasiado frágiles)
- Coverage target: 70%+ en módulos nuevos (establecer en CI)
