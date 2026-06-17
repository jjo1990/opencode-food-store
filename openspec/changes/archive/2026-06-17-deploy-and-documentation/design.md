## Context

Food Store está completo a nivel funcional. Este change es el paso final de pulido para deploy y entrega. Resuelve 4 bugs críticos que bloquean cualquier deploy y prepara la documentación, CI/CD, y configuración de plataforma.

## Goals / Non-Goals

- ✅ El proyecto debe poder ejecutarse desde cero siguiendo únicamente los READMEs
- ✅ `docker-compose up --build` debe funcionar sin errores
- ✅ CI/CD debe correr en cada push/PR
- ❌ No se modifica lógica de negocio ni se agregan features nuevos
- ❌ No se genera el video de demostración (placeholder en README)

## Decisions

### D1: Frontend Dockerfile — Flat Structure

**Problema**: El Dockerfile actual asume estructura monorepo (`apps/frontend/`, `packages/`, `turbo.json`) que no existe.

**Decisión**: Reescribir como multi-stage build simple:
```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Build context**: Debe ser `.` (raíz del proyecto), no `./frontend`. El `docker-compose.yml` se actualiza en consecuencia:
```yaml
frontend:
  build:
    context: .
    dockerfile: frontend/Dockerfile
```

**nginx.conf**: Actualizar `root /app/dist` → `root /usr/share/nginx/html`.

### D2: SECRET_KEY → JWT_SECRET_KEY

**Problema**: `backend/app/core/config.py:9` lee `os.getenv("JWT_SECRET_KEY", ...)` pero `backend/.env.example:2` define `SECRET_KEY=...`. Cualquier deploy nuevo usa el default inseguro.

**Decisión**: Renombrar en `.env.example`. La variable en `config.py` ya es `JWT_SECRET_KEY` — es la fuente de verdad. No se modifica código, solo el archivo de ejemplo.

**Archivos afectados**:
- `backend/.env.example`: `SECRET_KEY` → `JWT_SECRET_KEY`
- `README.md:121`: Actualizar referencia en sección de variables de entorno
- `docs/Integrador.txt:329`: Actualizar nombre de variable en tabla 10.1

### D3: requirements.txt — Runtime Dependencies

**Problema**: Faltan 7 dependencias runtime. `pip install -r requirements.txt` instala solo 11 paquetes de los ~20+ necesarios.

**Decisión**: Agregar los paquetes faltantes con version pins razonables:
```
sqlmodel==0.0.14
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
slowapi==0.1.9
alembic==1.12.1
email-validator==2.1.0
python-multipart==0.0.6
```

**No se agregan**: pytest, httpx, pytest-asyncio, pytest-cov ya están incluidos.

### D4: Root .env.example — Minimal Reference

**Problema**: El archivo raíz duplica variables (`DATABASE_URL`, `SECRET_KEY`, `DEBUG`) que ya están en `backend/.env.example` y usa `REACT_APP_API_URL` que Vite no reconoce.

**Decisión**: Reemplazar por versión mínima que:
1. Referencia a `backend/.env.example` y `frontend/.env.example` como fuente de verdad
2. Solo incluye variables específicas de Docker Compose (`POSTGRES_*`)

### D5: CI/CD — GitHub Actions

**Decisión**: Workflow simple con 2 jobs paralelos:
- `backend`: Instala dependencias y corre `pytest`
- `frontend`: Instala dependencias y corre `tsc --noEmit`

Sin servicios (Postgres, Redis) — los tests usan SQLite en memoria.

### D6: Procfile — PaaS Deploy

**Decisión**: Procfile estándar para Railway/Render:
```
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Usa `${PORT:-8000}` para respetar la variable de entorno que inyecta la plataforma, con fallback a 8000 para desarrollo local.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| `npm install` sin lockfile en Docker puede instalar versiones inconsistentes | El stage de build aísla el problema; en CI usamos `npm ci` con lockfile |
| Los tests CI corren sin PostgreSQL real (SQLite) | Los tests unitarios usan SQLite en memoria por diseño; tests de integración MP requieren secrets y no corren en CI básico |
| El Procfile expone backend sin frontend servido | Las plataformas PaaS típicamente sirven el frontend separado (Vercel/Netlify) o con nginx interno |

## Migration Plan

1. Aplicar todos los fixes de configuración (no rompen nada existente)
2. Verificar `docker-compose build`
3. Ejecutar `pytest` y `tsc --noEmit`
4. Commit y push

No se requiere migración de datos ni downtime.

## Open Questions

- ¿URL del repositorio público? (para CE-01)
- ¿Link real del video? (placeholder en README hasta que esté disponible)
- ¿Credenciales de MercadoPago para el entorno de producción? (sandbox por ahora)
