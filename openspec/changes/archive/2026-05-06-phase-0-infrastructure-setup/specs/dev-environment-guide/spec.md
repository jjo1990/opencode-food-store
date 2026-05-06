## Requisito: Documentación de Entorno de Desarrollo

### Descripción

Guía completa para que cualquier developer nuevo (o el mismo después de 6 meses) sepa exactamente cómo clonar, instalar y correr la aplicación localmente. Sin fricción, sin "funciona en mi máquina".

### Requisitos Funcionales

1. **DEV_SETUP.md** incluye:
   - **Requisitos previos**: versiones exactas de Node, Python, Docker, Git
   - **Quick start**: 5 pasos máximo para estar corriendo
   - **Setup detallado**: paso a paso, con comandos copiables
   - **Troubleshooting**: problemas comunes y soluciones
   - **Convenciones**: naming, commit messages, file structure
   - **Common commands**: cheat sheet de comandos frecuentes
2. **Diagrama ASCII** mostrando:
   - Estructura de directorios (monorepo layout)
   - Archivos importantes y su propósito
3. **Secciones específicas**:
   - Frontend setup (Node, npm, Vite)
   - Backend setup (Python, venv, pip, Alembic)
   - Database setup (Postgres, migrations, seed)
   - Docker alternative (docker-compose up)
4. **Scripts helpers** (opcional):
   - `scripts/setup.sh` — automatiza setup (Linux/Mac)
   - `scripts/setup.ps1` — automatiza setup (Windows PowerShell)
5. **Version matrix** documentando versiones testeadas:
   - Node 18.x, 20.x
   - Python 3.11, 3.12
   - PostgreSQL 15, 16
   - Docker Desktop (versión mínima)

### Requisitos No-Funcionales

1. Setup debe poder completarse en < 15 minutos (sin Docker build)
2. Documentación debe ser clara para alguien sin conocimiento previo
3. Troubleshooting debe resolver 90% de issues comunes
4. Documentación debe ser mantenible (links no romperse)
5. Screenshots o diagramas deben ser útiles (no noise)

### Criterio de Aceptación

- ✅ Developer nuevo sigue DEV_SETUP.md sin ayuda y logra: `docker-compose up`
- ✅ Frontend accesible en `http://localhost:5173`
- ✅ Backend Swagger accesible en `http://localhost:8000/docs`
- ✅ Database connection funciona
- ✅ `npm run test` y `pytest` pasan en primer intento
- ✅ Troubleshooting resuelve al menos 5 problemas comunes

### Referencias Técnicas

**Files creados/modificados:**

- `DEV_SETUP.md` (root) — main documentation
- `CONTRIBUTING.md` (root) — contribution guidelines
- `scripts/setup.sh` (root, optional)
- `scripts/setup.ps1` (root, optional)
- `TROUBLESHOOTING.md` (root, optional)

**Estructura recomendada de DEV_SETUP.md:**

```markdown
# Development Setup Guide

## Quick Start (5 steps)

1. Clone...
2. Docker compose up...
3. Etc.

## Requirements

- Node 18+
- Python 3.11+
- Docker Desktop

## Detailed Setup

### Frontend

### Backend

### Database

### Docker

## Monorepo Structure
```

frontend/
├── src/
│ ├── components/
│ ├── features/
│ ├── pages/
│ └── hooks/
backend/
├── app/
│ ├── modules/
│ ├── core/
│ └── db/
openspec/
├── changes/
└── specs/

````

## Common Commands
```bash
npm run dev       # Start frontend + backend
npm run test      # Run tests
npm run lint      # Check linting
````

## Troubleshooting

- Docker won't start: ...
- Port 5173 already in use: ...
- Postgres connection error: ...

## Conventions

- Commits: conventional commits
- Branches: feature/_, bugfix/_, hotfix/\*
- File naming: camelCase (JS), snake_case (Python)

```

**Convenciones de documentación:**
- Lenguaje: Rioplatense (voseo)
- Código en markdown con syntax highlighting
- Links verificados (dead links = bad DX)
- Secciones colapsables para detalles
```
