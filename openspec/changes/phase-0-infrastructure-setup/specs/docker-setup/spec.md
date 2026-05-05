## Requisito: Docker Setup y docker-compose

### Descripción

Containerizar la aplicación para reproducibilidad total. `docker-compose.yml` levanta PostgreSQL, backend FastAPI y frontend React en desarrollo local sin fricción. Dockerfile multi-stage para builds de producción optimizados.

### Requisitos Funcionales

1. **docker-compose.yml** define 3 servicios:
   - `postgres`: Imagen oficial PostgreSQL 15
   - `backend`: FastAPI en puerto 8000
   - `frontend`: React dev server en puerto 5173
2. **Dockerfile frontend** multi-stage:
   - Build stage: Node 18 + npm install + build
   - Serve stage: nginx para servir SPA
3. **Dockerfile backend** optimizado:
   - Python 3.11 slim
   - pip install con caching
   - CMD: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. **.dockerignore** excluye: node_modules/, .git/, .env, etc.
5. **Volume mounts** en dev:
   - Backend: código fuente montado para hot-reload
   - Frontend: node_modules y build artifacts NOT montados (para evitar inconsistencias)
6. **Environment variables**:
   - `.env.example` define todas las variables necesarias
   - `docker-compose.yml` usa `.env` (creado por el usuario)

### Requisitos No-Funcionales

1. `docker-compose up` debe completar < 2 minutos (incluyendo build first time)
2. Segundo `docker-compose up` debe ser < 30s (caché de layers)
3. Dockerfile layers deben seguir best practices (frequent changes last)
4. Imágenes deben ser relativamente pequeñas: frontend < 100MB, backend < 400MB

### Criterio de Aceptación

- ✅ `docker-compose up` levanta los 3 servicios correctamente
- ✅ Frontend accessible en `http://localhost:5173`
- ✅ Backend accessible en `http://localhost:8000/docs`
- ✅ PostgreSQL accessible desde backend (connection string funciona)
- ✅ `docker-compose down` detiene y limpia contenedores
- ✅ Cambios en código Python/TypeScript son hot-reloadeados
- ✅ `docker-compose logs` muestra output de todos los servicios

### Referencias Técnicas

**Files creados/modificados:**
- `Dockerfile` (root, multi-stage)
- `frontend/Dockerfile` (opcional si queremos build separado)
- `backend/Dockerfile` (opcional si queremos build separado)
- `docker-compose.yml` (root)
- `docker-compose.override.yml` (root, para dev overrides)
- `.dockerignore`
- `db-init.sql` (inicializar DB)
- `.env.example` (template de variables)

**Servicios en docker-compose:**
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: foodstore
      POSTGRES_PASSWORD: devpass
      POSTGRES_DB: foodstore_db
    volumes:
      - ./db-init.sql:/docker-entrypoint-initdb.d/init.sql
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgresql://foodstore:devpass@postgres:5432/foodstore_db
      - SECRET_KEY=dev-secret-key-only-for-local
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app/backend

  frontend:
    build:
      context: frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
```

**Convenciones:**
- Servicios nombrados lowercase (postgres, backend, frontend)
- Puertos mapeados: 5432 (Postgres), 8000 (FastAPI), 5173 (Vite)
- Volúmenes nombrados vs bind mounts (usar named para datos persistentes)
- Health checks no son necesarios en dev (pero recomendados en prod)
