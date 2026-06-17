# Food Store — Backend

FastAPI + SQLModel + PostgreSQL

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in values:
   ```bash
   cp .env.example .env
   ```

4. Run migrations:
   ```bash
   alembic upgrade head
   ```

5. Seed data:
   ```bash
   python -m app.db.seed
   ```

6. Start server:
   ```bash
   uvicorn app.main:app --reload
   ```

7. API docs at http://localhost:8000/docs

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://user:pass@localhost:5432/foodstore` |
| `JWT_SECRET_KEY` | Secret key for JWT signing (min 32 chars) | `your-secret-key` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry in minutes | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry in days | `7` |
| `MP_ACCESS_TOKEN` | MercadoPago access token | `TEST-xxxx` |
| `MP_PUBLIC_KEY` | MercadoPago public key | `TEST-xxxx` |
| `MP_WEBHOOK_SECRET` | MercadoPago webhook secret | `TEST-xxxx` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:5173` |
| `ENVIRONMENT` | Environment mode | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Architecture

```
Router → Service → UoW → Repository → Model
```

- `app/core/` — UoW, BaseRepository, config, security, logging
- `app/auth/` — JWT authentication + RBAC
- `app/usuarios/` — User CRUD
- `app/productos/` — Product catalog
- `app/categorias/` — Hierarchical categories
- `app/ingredientes/` — Ingredients + allergens
- `app/pedidos/` — 6-state FSM + audit trail
- `app/pagos/` — MercadoPago Checkout + IPN webhooks
- `app/direcciones/` — Delivery addresses
- `app/admin/` — Admin dashboard
- `app/checkout/` — Checkout validation

## Testing

```bash
python -m pytest -v
```

Tests use SQLite in-memory database — no PostgreSQL needed.
