## 1. Módulo Checkout

- [x] 1.1 Crear `backend/app/checkout/__init__.py` con export del router
- [x] 1.2 Crear `backend/app/checkout/schemas.py` con ValidarRequest, ItemValidado, ValidarResponse
- [x] 1.3 Crear `backend/app/checkout/service.py` con CheckoutService.validar(items)
- [x] 1.4 Crear `backend/app/checkout/router.py` con POST /checkout/validar

## 2. Integración

- [x] 2.1 Registrar router en `backend/app/main.py`
- [x] 2.2 Verificar imports

## 3. Verify

- [x] 3.1 Test de integración: `python -c "from app.checkout import router; print('OK')"`
