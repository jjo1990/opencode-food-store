## 1. Modelo y Migración

- [x] 1.1 Crear `backend/app/models/direccion_entrega.py` con modelo DireccionEntrega (id, usuario_id FK, alias, calle, numero, piso, departamento, ciudad, codigo_postal, referencia, es_principal, + timestamps + soft_delete)
- [x] 1.2 Agregar `DireccionEntrega` al `__all__` de `backend/app/models/__init__.py`
- [x] 1.3 Generar migración Alembic autogenerate y verificar que cree `direccion_entrega` con partial unique index

## 2. Módulo Direcciones

- [x] 2.1 Crear `backend/app/direcciones/__init__.py` con export del router
- [x] 2.2 Crear `backend/app/direcciones/schemas.py` con DireccionCreate, DireccionUpdate, DireccionResponse (Pydantic)
- [x] 2.3 Crear `backend/app/direcciones/repository.py` con DireccionRepository (CRUD + count_active_by_user + get_principal)
- [x] 2.4 Crear `backend/app/direcciones/service.py` con DireccionService (validaciones: ownership, única principal, no eliminar única dirección)
- [x] 2.5 Crear `backend/app/direcciones/router.py` con 6 endpoints (POST, GET list, GET by id, PUT, PATCH principal, DELETE)

## 3. Integración

- [x] 3.1 Registrar router en `backend/app/main.py` con `app.include_router(direcciones_router, prefix="/api/v1")`
- [x] 3.2 Verificar imports y que no haya errores de dependencia circular
- [x] 3.3 Ejecutar `alembic upgrade head` para aplicar migración

## 4. Verificación

- [x] 4.1 Verificar que la migración se aplica correctamente (check tabla en BD)
- [x] 4.2 Verificar que los endpoints responden correctamente con autenticación
- [x] 4.3 Verificar que ownership funciona (usuario A no ve direcciones de usuario B)
