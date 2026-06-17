## ADDED Requirements

### Requirement: Docker build MUST succeed for both services

El proyecto debe incluir Dockerfiles funcionales para backend y frontend. `docker-compose build` MUST completar sin errores. El frontend Dockerfile MUST usar estructura flat (no monorepo). El backend Dockerfile MUST instalar todas las dependencias desde `requirements.txt`.

#### Scenario: docker-compose build completado

- **GIVEN** el proyecto clonado en una máquina con Docker instalado
- **WHEN** se ejecuta `docker-compose build`
- **THEN** ambos servicios (backend y frontend) se construyen sin errores
- **AND** el frontend queda servido por nginx en puerto 80

#### Scenario: frontend Dockerfile estructura flat

- **GIVEN** el `frontend/Dockerfile`
- **WHEN** se inspecciona su contenido
- **THEN** no contiene referencias a `apps/frontend`, `packages/`, ni `turbo.json`
- **AND** usa `COPY frontend/` con contexto de build en raíz del proyecto

---

### Requirement: Environment variables MUST be correctly named

La variable para la clave secreta JWT MUST llamarse `JWT_SECRET_KEY` (no `SECRET_KEY`) en `backend/.env.example`, consistente con `backend/app/core/config.py:9`. El `docker-compose.yml` MUST usar `VITE_API_URL` (no `REACT_APP_API_URL`) para el frontend.

#### Scenario: JWT_SECRET_KEY en backend/.env.example

- **GIVEN** `backend/.env.example`
- **WHEN** se lee el archivo
- **THEN** contiene `JWT_SECRET_KEY=cambia-esto-por-una-clave-de-64-caracteres-minimo`
- **AND** no contiene `SECRET_KEY=` (sin prefijo JWT)

#### Scenario: VITE_API_URL en docker-compose.yml

- **GIVEN** `docker-compose.yml`
- **WHEN** se inspecciona la sección `frontend.environment`
- **THEN** contiene `VITE_API_URL` (no `REACT_APP_API_URL`)

#### Scenario: root .env.example minimal

- **GIVEN** el `.env.example` raíz
- **WHEN** se lee el archivo
- **THEN** referencia a `backend/.env.example` y `frontend/.env.example`
- **AND** no contiene `REACT_APP_API_URL`
- **AND** solo incluye variables de Docker Compose (`POSTGRES_*`)

---

### Requirement: requirements.txt MUST include all runtime dependencies

`backend/requirements.txt` MUST incluir todos los paquetes necesarios para ejecutar el backend. Un `pip install -r requirements.txt` seguido de `uvicorn app.main:app` MUST iniciar el servidor sin `ModuleNotFoundError`.

#### Scenario: pip install completo

- **GIVEN** un entorno virtual Python 3.11 limpio
- **WHEN** se ejecuta `pip install -r backend/requirements.txt`
- **THEN** no hay errores de dependencias faltantes
- **AND** el servidor puede iniciarse con `uvicorn app.main:app`

#### Scenario: paquetes requeridos presentes

- **GIVEN** `backend/requirements.txt`
- **WHEN** se inspecciona el archivo
- **THEN** contiene `sqlmodel`, `python-jose`, `passlib`, `slowapi`, `alembic`, `email-validator`, `python-multipart`
- **AND** cada paquete tiene un version pin

---

### Requirement: Each layer MUST have a README.md with setup instructions

`backend/README.md` y `frontend/README.md` MUST existir con instrucciones paso a paso para configurar y ejecutar cada capa desde cero.

#### Scenario: backend/README.md existe

- **GIVEN** el directorio `backend/`
- **WHEN** se lista su contenido
- **THEN** existe `README.md`
- **AND** contiene instrucciones para: virtual environment, pip install, .env, alembic upgrade, seed, uvicorn

#### Scenario: frontend/README.md existe

- **GIVEN** el directorio `frontend/`
- **WHEN** se lista su contenido
- **THEN** existe `README.md`
- **AND** contiene instrucciones para: npm install, .env, npm run dev

---

### Requirement: CI/CD workflow MUST run backend tests and frontend type-check

Un workflow de GitHub Actions MUST ejecutarse en cada push y pull request. El job de backend MUST correr `pytest`. El job de frontend MUST correr `tsc --noEmit`.

#### Scenario: workflow triggers en push y PR

- **GIVEN** `.github/workflows/tests.yml`
- **WHEN** se inspecciona el archivo
- **THEN** el trigger es `on: [push, pull_request]`
- **AND** contiene jobs separados para `backend` y `frontend`

#### Scenario: backend job ejecuta pytest

- **GIVEN** el workflow de CI
- **WHEN** se ejecuta el job `backend`
- **THEN** instala dependencias con `pip install -r requirements.txt`
- **AND** ejecuta `python -m pytest -v`

#### Scenario: frontend job ejecuta type-check

- **GIVEN** el workflow de CI
- **WHEN** se ejecuta el job `frontend`
- **THEN** instala dependencias con `npm ci`
- **AND** ejecuta `npx tsc --noEmit`

---

### Requirement: Swagger UI MUST include project metadata

La instancia de FastAPI en `backend/app/main.py` MUST configurarse con `title`, `version`, `description`, `contact` y `license_info` para que la documentación Swagger en `/docs` muestre información del proyecto.

#### Scenario: Swagger muestra metadata

- **GIVEN** el servidor backend corriendo
- **WHEN** se accede a `http://localhost:8000/docs`
- **THEN** el título es "Food Store API"
- **AND** la versión es "0.0.1"
- **AND** incluye descripción y licencia MIT

---

### Requirement: Procfile MUST enable one-click deploy on PaaS platforms

Debe existir un `Procfile` en la raíz del proyecto que inicie el backend con `uvicorn` usando el puerto de la variable de entorno `PORT`.

#### Scenario: Procfile existe y es válido

- **GIVEN** la raíz del proyecto
- **WHEN** se lista el contenido
- **THEN** existe `Procfile`
- **AND** contiene `web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
