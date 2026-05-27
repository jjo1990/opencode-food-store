## 1. Setup y Modelo

- [x] 1.1 Instalar SDK mercadopago: `pip install mercadopago` y agregar a requirements.txt
- [x] 1.2 Crear modelo `Pago` en `backend/app/models/pago.py` con campos: id (UUID), pedido_id (FK), mp_payment_id (String, nullable, unique), mp_status (String), external_reference (String, unique), idempotency_key (String, unique), created_at. Relación con Pedido.
- [x] 1.3 Actualizar `backend/app/models/__init__.py` para exportar Pago
- [x] 1.4 Actualizar `backend/app/models/pedido.py` para agregar relación `pagos = relationship("Pago", back_populates="pedido")`
- [x] 1.5 Agregar `MP_ACCESS_TOKEN` al archivo `backend/app/core/config.py`

## 2. Migración

- [x] 2.1 Generar migración Alembic: `alembic revision --autogenerate -m "add_pago_table"`
- [x] 2.2 Verificar que la migración incluye la tabla `pago` con columnas correctas y FK a pedido

## 3. Módulo Pagos

- [x] 3.1 Crear `backend/app/pagos/__init__.py` exportando router
- [x] 3.2 Crear `backend/app/pagos/schemas.py` con: CrearPagoRequest (pedido_id, card_token), PagoResponse (mp_payment_id, status, status_detail)
- [x] 3.3 Crear `backend/app/pagos/service.py` con PagoService:
  - Inicializa SDK de MercadoPago con MP_ACCESS_TOKEN desde config
  - crear_pago(): valida pedido, genera idempotency_key, llama a MP SDK, registra en BD, retorna respuesta
  - Manejo de idempotencia (detectar duplicados por idempotency_key)
- [x] 3.4 Crear `backend/app/pagos/router.py` con endpoint `POST /api/v1/pagos/crear` protegido con require_role("CLIENT")

## 4. Integración

- [x] 4.1 Registrar `pagos_router` en `backend/app/main.py`
- [x] 4.2 Verificar imports: `python -c "from app.pagos.router import router"` sin errores
- [x] 4.3 Verificar que el SDK se importa correctamente: `python -c "import mercadopago; print('OK')"`
