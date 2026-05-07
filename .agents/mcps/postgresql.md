# PostgreSQL MCP

**Model Context Protocol for PostgreSQL Database Management**

## Overview

This MCP provides direct database access to PostgreSQL for schema inspection, query execution, and migration verification.

## Features

- **Schema Inspection**: List tables, columns, constraints, indexes
- **Query Execution**: Run SELECT queries for data inspection and analysis
- **Migration Verification**: Check migration status and history (via Alembic)
- **Performance Analysis**: Query optimization suggestions, index recommendations

## Configuration

### Environment Variables

```env
DATABASE_URL=postgresql://food_store_user:food_store_password@localhost:5432/food_store
DB_SCHEMA=public
```

### Connection Details

- **Host**: localhost (local development)
- **Port**: 5432
- **Database**: food_store
- **User**: food_store_user
- **Password**: food_store_password (from docker-compose)

## Common Operations

### Schema Inspection

```bash
# List all tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

# List columns for a table
SELECT column_name, data_type, is_nullable FROM information_schema.columns 
WHERE table_name = 'users';

# List indexes
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'users';

# List constraints
SELECT constraint_name, constraint_type FROM information_schema.table_constraints
WHERE table_name = 'users';
```

### Data Inspection

```bash
# Count records in a table
SELECT COUNT(*) FROM users;

# View recent records
SELECT * FROM users ORDER BY created_at DESC LIMIT 10;

# Check for duplicates
SELECT column_name, COUNT(*) FROM users GROUP BY column_name HAVING COUNT(*) > 1;
```

### Migration Verification

```bash
# Check Alembic migration status
alembic current

# View migration history
alembic history --verbose

# Check pending migrations
alembic check
```

## Integration with Food Store

### Key Tables

- **users**: User accounts, authentication, roles
- **categories**: Product categories (hierarchical)
- **products**: Product catalog with stock tracking
- **cart_items**: Shopping cart state
- **orders**: Order records with FSM status
- **order_items**: Line items for orders
- **payment_transactions**: MercadoPago integration records
- **user_addresses**: Delivery addresses
- **audit_logs**: System audit trail

### Phase 1 (Authentication) Tables

Primary tables:
- `users` (id, email, password_hash, role, created_at, updated_at)
- `refresh_tokens` (id, user_id, token, expires_at)
- `audit_logs` (id, user_id, action, timestamp)

## Best Practices

1. **Read-Only Queries First**: Always use SELECT to inspect before making changes
2. **Check Constraints**: Verify foreign key relationships before deleting
3. **Verify Migrations**: Run `alembic check` before applying migrations
4. **Backup Before Changes**: Always back up production databases
5. **Use Transactions**: Group related changes with BEGIN/COMMIT

## Troubleshooting

### Connection Issues

```bash
# Test connection
psql -h localhost -U food_store_user -d food_store -c "SELECT 1;"
```

### Migration Conflicts

```bash
# Check current migration version
alembic current

# If downgrade needed
alembic downgrade -1

# Re-apply
alembic upgrade head
```

### Performance Issues

```bash
# Find slow queries
SELECT query, calls, total_time FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;

# Check table bloat
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables WHERE schemaname = 'public';
```

## When to Use This MCP

- ✅ Inspecting schema after migrations
- ✅ Verifying data integrity before/after features
- ✅ Checking migration status
- ✅ Writing analytics queries
- ✅ Performance analysis
- ❌ Don't use for: Direct production data manipulation (use migrations instead)

## See Also

- `backend/pyproject.toml` — SQLModel, alembic dependencies
- `backend/app/db/` — ORM models and migrations
- `docs/Integrador.txt` — Data model documentation
