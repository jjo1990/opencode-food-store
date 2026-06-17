## Why

Food Store está a un paso de producción. Todos los features están implementados, testeados, y la arquitectura es sólida. Pero hay **4 bugs críticos que bloquean el deploy** y falta la documentación de entrega. Si no se corrigen, el sistema no puede ejecutarse desde cero en una máquina limpia, ni con Docker, ni en plataformas PaaS.

Los 4 bugs críticos:

1. **El `.env.example` del backend usa `SECRET_KEY` pero `config.py` lee `JWT_SECRET_KEY`** — esto rompe la autenticación JWT en cualquier deploy nuevo. El token se firma con `dev-secret-key-change-in-production` (el default), no con lo que el usuario configure.
2. **El `Dockerfile` del frontend asume estructura monorepo** (`apps/frontend`, `packages/`) que no existe en el proyecto flat actual. `docker-compose build` falla.
3. **`requirements.txt` está incompleto** — le faltan `sqlmodel`, `python-jose`, `passlib`, `slowapi`, `alembic`, `email-validator` y `python-multipart`. El backend no arranca tras `pip install -r requirements.txt`.
4. **El `.env.example` raíz tiene `REACT_APP_API_URL`** — Vite no lee ese prefijo, necesita `VITE_API_URL`. Además lista variables duplicadas que ya están en los `.env.example` por capa.

Además, la entrega requiere documentación completa, CI/CD, soporte Docker funcional, Procfile para PaaS, y metadatos Swagger.

## What Changes

- **Fix `backend/.env.example`**: Renombrar `SECRET_KEY` → `JWT_SECRET_KEY`. Agregar `ENVIRONMENT` y `LOG_LEVEL`.
- **Fix `root .env.example`**: Reemplazar por versión mínima que referencie los archivos por capa.
- **Fix `backend/requirements.txt`**: Agregar `sqlmodel`, `python-jose[cryptography]`, `passlib[bcrypt]`, `slowapi`, `alembic`, `email-validator`, `python-multipart`.
- **Fix `frontend/Dockerfile`**: Reescribir para estructura flat (no monorepo). Multi-stage: build con Node 20, serve con nginx.
- **Fix `frontend/nginx.conf`**: Actualizar `root` a `/usr/share/nginx/html`.
- **Fix `docker-compose.yml`**: Cambiar `REACT_APP_API_URL` → `VITE_API_URL`. Ajustar build context del frontend.
- **Crear `backend/README.md`**: Instrucciones de setup (venv, pip install, alembic, seed, uvicorn).
- **Crear `frontend/README.md`**: Instrucciones de setup (npm install, .env, npm run dev).
- **Crear `Procfile`**: Para deploy en Railway/Render.
- **Crear `.github/workflows/tests.yml`**: CI/CD con pytest y tsc --noEmit.
- **Crear `LICENSE`**: MIT.
- **Actualizar `root README.md`**: Sección de deploy, arquitectura, video placeholder, fix SECRET_KEY → JWT_SECRET_KEY.
- **Agregar metadatos Swagger**: `title`, `version`, `description`, `contact`, `license_info` en `backend/app/main.py`.
- **Actualizar `docs/Integrador.txt`**: Checklist de entrega con estados actualizados.

## Capabilities

### New Capabilities

- `deploy-readiness`: El proyecto puede desplegarse en Docker, Railway/Render, o localmente desde cero con instrucciones documentadas.
- `ci-cd`: GitHub Actions ejecuta tests de backend y type-check de frontend en cada push y PR.

### Modified Capabilities

- `backend-config`: `.env.example` corregido para que `JWT_SECRET_KEY` coincida con `config.py`.
- `frontend-docker`: Dockerfile funcional para estructura flat.

## Impact

- **Backend**: `.env.example`, `requirements.txt`, `app/main.py`, `README.md` (nuevo)
- **Frontend**: `Dockerfile`, `nginx.conf`, `README.md` (nuevo)
- **Raíz**: `.env.example`, `README.md`, `docker-compose.yml`, `Procfile` (nuevo), `LICENSE` (nuevo)
- **CI/CD**: `.github/workflows/tests.yml` (nuevo)
- **Docs**: `docs/Integrador.txt` (checklist actualizado)
- **Seguridad**: Sin impacto. No se exponen secretos.
- **Dependencias**: Sin cambios funcionales. Solo fixes de configuración.
