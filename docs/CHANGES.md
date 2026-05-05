# Mapa de Changes — Food Store v5.0

## Desarrollo Spec-Driven (SDD) — Sprint 0 a Sprint N

### Visión General

Este documento define el **mapa completo de changes** para desarrollar Food Store desde cero. Cada change es una unidad independiente con:

- **Nombre** (kebab-case): identificador único
- **Funcionalidad**: qué comportamiento del negocio implementa
- **Historias de Usuario**: qué US están cubiertas
- **Dependencias**: de qué otros changes depende (y por qué)
- **Estimación**: horas de desarrollo

El orden es **secuencial pero flexible**: podés paralelizar changes que no tengan dependencias.

---

## SPRINT 0: Infraestructura Base

> Sin estos changes, nada funciona. Son la fundación.

### Change #1: `setup-monorepo-estructura`

- **Historias**: US-000
- **Funcionalidad**: Crear la estructura de carpetas, Git inicial, README.md y documentación base
- **Backend**: Carpetas feature-first (`auth/`, `usuarios/`, `productos/`, etc.)
- **Frontend**: Carpetas FSD (`app/`, `pages/`, `features/`, `entities/`, `shared/`)
- **Artefactos**: `.gitignore`, `README.md`, `.env.example` (ambos lados)
- **Dependencias**: Ninguna
- **Estimación**: 2-3 horas

---

### Change #2: `backend-setup-fastapi-dependencies`

- **Historias**: US-000a
- **Funcionalidad**: Configurar FastAPI, SQLModel, Alembic, rate limiting (slowapi) y dependencias core
- **Backend**:
  - `main.py` con CORS middleware, rate limiting middleware, registro de routers
  - `core/config.py` (lectura de variables de entorno)
  - `core/database.py` (engine, session factory)
  - `core/security.py` (hashing, JWT utilities)
  - `requirements.txt` con todas las dependencias
- **Testing**: Swagger UI en `/docs` y `/redoc` accesible sin errores
- **Dependencias**: Change #1
- **Estimación**: 3-4 horas

---

### Change #3: `backend-setup-database-alembic-seed`

- **Historias**: US-000b
- **Funcionalidad**: PostgreSQL, Alembic config, migraciones y seed data obligatorio
- **Backend**:
  - `alembic/` con directorio de versiones vacío
  - Modelos SQLModel completos (todas las entidades del ERD v5)
  - Script `app/db/seed.py` que carga roles, estados de pedido, formas de pago y admin inicial
  - Primera migración autogenerada con `alembic revision --autogenerate`
- **Testing**:
  - `alembic upgrade head` sin errores
  - `python -m app.db.seed` carga datos iniciales
  - Seed es idempotente: ejecutar 2 veces no duplica datos
- **Dependencias**: Change #2
- **Estimación**: 4-5 horas

---

### Change #4: `frontend-setup-react-vite-dependencies`

- **Historias**: US-000c
- **Funcionalidad**: React + TypeScript + Vite + librerías core (TanStack Query, TanStack Form, Zustand, Axios, Tailwind)
- **Frontend**:
  - `vite.config.ts` (React plugin, SWC fast refresh)
  - `tsconfig.json` (strict: true)
  - `tailwind.config.js` + PostCSS
  - `package.json` con todas las dependencias
  - `.env.example` con `VITE_API_BASE_URL` y `VITE_MERCADOPAGO_PUBLIC_KEY`
- **Testing**:
  - `npm install` sin errores
  - `npm run dev` arranca en puerto 5173
  - Verificar TypeScript en modo estricto
- **Dependencias**: Change #1
- **Estimación**: 2-3 horas

---

### Change #5: `backend-patterns-infrastructure-base`

- **Historias**: US-000d
- **Funcionalidad**: BaseRepository genérico, Unit of Work, dependencias de FastAPI (get_current_user, require_role), error handling RFC 7807
- **Backend**:
  - `core/patterns.py`: BaseRepository[T] genérico con CRUD base
  - `core/uow.py`: Unit of Work como context manager (`async with`)
  - `core/dependencies.py`: get_current_user, require_role factory
  - `core/exceptions.py`: HTTPException handlers RFC 7807
- **Testing**:
  - UoW entra y sale sin excepciones ✓
  - UoW rollback en error ✓
  - require_role lanza 403 ✓
  - Errores son RFC 7807 ✓
- **Dependencias**: Change #3
- **Estimación**: 5-6 horas (patrón complejo)

---

### Change #6: `frontend-zustand-stores-setup`

- **Historias**: US-000e
- **Funcionalidad**: Configurar los 4 stores de Zustand (authStore, cartStore, paymentStore, uiStore) con persistencia selectiva
- **Frontend**:
  - `shared/stores/authStore.ts`: auth con persist localStorage
  - `shared/stores/cartStore.ts`: carrito con persist localStorage
  - `shared/stores/paymentStore.ts`: estado de pago SIN persist
  - `shared/stores/uiStore.ts`: UI global SIN persist
- **Testing**:
  - Verificar persistencia: localStorage tiene claves correctas
  - Verificar que authStore solo guarda tokens (no user completo)
  - Verificar que cartStore persiste items
- **Dependencias**: Change #4
- **Estimación**: 3 horas

---

### Change #7: `frontend-axios-interceptors-setup`

- **Historias**: US-066 (token expirado)
- **Funcionalidad**: Configurar Axios con interceptores JWT y refresh automático
- **Frontend**:
  - `shared/api/axios.ts`: instancia Axios centralizada
  - Interceptor request: adjunta Authorization: Bearer
  - Interceptor response: detecta 401, llama refresh, reintenta
  - Cola de requests pendientes durante refresh
- **Testing**:
  - Token expira → interceptor lo detecta → refresh automático
  - Verificar que usuario NO ve errores intermitentes
  - Verificar que requests se encolan durante refresh
- **Dependencias**: Change #6
- **Estimación**: 3-4 horas

---

## SPRINT 1: Autenticación y Autorización

### Change #8: `auth-user-registration`

- **Historias**: US-001
- **Funcionalidad**: Registro de cliente con validaciones y asignación automática de rol CLIENT
- **Backend**:
  - Router: `POST /api/v1/auth/register`
  - Service: validar email único, hashear contraseña, crear usuario con rol CLIENT
  - Repository: UserRepository.create()
- **Frontend**: (será en otro change)
- **Validaciones**: RN-AU01, RN-AU07, RN-DA04
- **Testing**:
  - Email duplicado → error 409
  - Contraseña < 8 caracteres → error 422
  - Rol CLIENT asignado automáticamente ✓
- **Dependencias**: Change #5
- **Estimación**: 2-3 horas

---

### Change #9: `auth-user-login-rate-limiting`

- **Historias**: US-002, US-073
- **Funcionalidad**: Login con JWT + refresh token + rate limiting (5 intentos / 15 min)
- **Backend**:
  - Router: `POST /api/v1/auth/login`
  - Service: validar email/contraseña, generar access + refresh tokens
  - Rate limiting con slowapi en el router
  - RefreshTokenRepository: crear registro en tabla RefreshToken
- **Validaciones**: RN-AU02, RN-AU06, RN-AU08
- **Testing**:
  - 5 logins fallidos → 6to intento = 429 ✓
  - Token expira en 30 min ✓
  - Refresh token expira en 7 días ✓
  - No diferencia "email no existe" vs "contraseña incorrecta" ✓
- **Dependencias**: Change #8
- **Estimación**: 3-4 horas

---

### Change #10: `auth-token-refresh-rotation`

- **Historias**: US-003
- **Funcionalidad**: Endpoint refresh con rotación de tokens y detección de replay attacks
- **Backend**:
  - Router: `POST /api/v1/auth/refresh`
  - Service: validar refresh token, revocarlo, emitir nuevos tokens
  - Si detecta reuso (replay) → revocar TODOS los tokens del usuario (RN-AU05)
- **Validaciones**: RN-AU04, RN-AU05
- **Testing**:
  - Token válido → nuevo access + refresh ✓
  - Token expirado → 401 ✓
  - Token reusado → todos revocados ✓
- **Dependencias**: Change #9
- **Estimación**: 2-3 horas

---

### Change #11: `auth-logout`

- **Historias**: US-004
- **Funcionalidad**: Logout revocando refresh token
- **Backend**:
  - Router: `POST /api/v1/auth/logout`
  - Service: marcar RefreshToken.revoked_at
- **Frontend**: (será en otro change)
- **Validaciones**: RN-AU04
- **Testing**: RefreshToken marcado como revocado ✓
- **Dependencias**: Change #10
- **Estimación**: 1 hora

---

### Change #12: `auth-rbac-roles`

- **Historias**: US-005, US-006
- **Funcionalidad**: RBAC con 4 roles, asignación de roles por admin, protección de rutas
- **Backend**:
  - Router: `PUT /api/v1/admin/users/:id/roles` (solo ADMIN)
  - Service: validar que ADMIN no se quite a sí mismo siendo único, asignar roles
  - require_role() dependency que verifica roles del usuario
  - Todas las rutas protegidas con @require_role()
- **Validaciones**: RN-RB01-RB10
- **Testing**:
  - Rol insuficiente → 403 ✓
  - Sin token → 401 ✓
  - Último ADMIN intenta quitarse ADMIN → error ✓
- **Dependencias**: Change #5, Change #9
- **Estimación**: 3-4 horas

---

### Change #13: `frontend-auth-ui-forms`

- **Historias**: US-001, US-002, US-004
- **Funcionalidad**: Páginas de login, registro y logout con TanStack Form
- **Frontend**:
  - `pages/LoginPage.tsx`
  - `pages/RegisterPage.tsx`
  - `features/auth/LoginForm.tsx` + validaciones
  - `features/auth/RegisterForm.tsx` + validaciones
  - `features/auth/ProtectedRoute.tsx` HOC para rutas privadas
  - Integración con authStore
- **Testing**:
  - Formularios validan en frontend
  - Login/registro funciona end-to-end
  - Token se guarda en authStore
- **Dependencias**: Change #6, Change #9
- **Estimación**: 4-5 horas

---

### Change #14: `frontend-navigation-rbac`

- **Historias**: US-075, US-076
- **Funcionalidad**: Navegación adaptada al rol (Sidebar/NavBar renderiza menú según rol)
- **Frontend**:
  - `widgets/Navigation.tsx`: renderiza menú según roles del authStore
  - `widgets/Sidebar.tsx`: panel lateral con opciones por rol
  - Route guards en `app/AppRoutes.tsx`
- **Testing**:
  - CLIENT ve: Catálogo, Mi Carrito, Mis Pedidos, Perfil
  - STOCK ve: Productos, Categorías, Stock
  - PEDIDOS ve: Panel Pedidos
  - ADMIN ve: todo
- **Dependencias**: Change #13
- **Estimación**: 2-3 horas

---

### Change #15: `frontend-error-handling-global`

- **Historias**: US-067
- **Funcionalidad**: Error boundaries y manejo global de errores HTTP
- **Frontend**:
  - `shared/components/ErrorBoundary.tsx`
  - Interceptor Axios que mapea códigos a mensajes
  - Toast system para notificaciones
- **Testing**: Error 400 → muestra detalles de validación, 403 → "Sin permisos", etc.
- **Dependencias**: Change #7
- **Estimación**: 2 horas

---

## SPRINT 2: Catálogo de Productos

### Change #16: `catalog-categories-hierarchical`

- **Historias**: US-007, US-008, US-009, US-010
- **Funcionalidad**: CRUD de categorías con jerarquía recursiva (padre-hijo) y validación de ciclos
- **Backend**:
  - Router: POST/PUT/GET/DELETE `/api/v1/categorias`
  - Service: validar padre-hijo, detectar ciclos con CTE
  - CategoriaRepository: buscar por parent_id, validar ciclos antes de actualizar
  - Soft delete: eliminado_en
- **Validaciones**: RN-CA01, RN-CA02, RN-CA03
- **Testing**:
  - Crear subcategoría ✓
  - Intentar crear ciclo (A padre B, B padre A) → error ✓
  - Listar árbol anidado ✓
  - Soft delete ✓
- **Dependencias**: Change #12 (RBAC)
- **Estimación**: 4-5 horas (CTE recursiva)

---

### Change #17: `catalog-ingredients-allergens`

- **Historias**: US-011, US-012, US-013, US-014
- **Funcionalidad**: CRUD de ingredientes con flag de alérgeno
- **Backend**:
  - Router: POST/PUT/GET/DELETE `/api/v1/ingredientes`
  - Service: validar unicidad de nombre
  - IngredienteRepository
- **Validaciones**: RN-CA07
- **Testing**: Crear ingrediente con es_alergeno=true ✓
- **Dependencias**: Change #12
- **Estimación**: 2 horas

---

### Change #18: `catalog-products-crud`

- **Historias**: US-015, US-020, US-021, US-022
- **Funcionalidad**: CRUD de productos con precio (DECIMAL), stock y disponibilidad
- **Backend**:
  - Router: POST/PUT/DELETE/PATCH `/api/v1/productos`
  - Service: validar precio >= 0, stock >= 0
  - ProductoRepository: actualizar_stock() atómico
  - Soft delete: eliminado_en
- **Validaciones**: RN-CA04, RN-CA05, RN-CA09
- **Testing**:
  - Crear producto con precio decimal ✓
  - Actualizar stock atomicamente ✓
  - Soft delete ✓
  - Stock nunca negativo ✓
- **Dependencias**: Change #12
- **Estimación**: 3-4 horas

---

### Change #19: `catalog-product-categorias-association`

- **Historias**: US-016
- **Funcionalidad**: Asociar productos a múltiples categorías (M2M)
- **Backend**:
  - Tabla pivote: ProductoCategoria
  - Router: PUT `/api/v1/productos/:id/categorias`
  - Service: asignar/desasignar categorías
- **Validaciones**: RN-CA06
- **Testing**: Un producto en múltiples categorías ✓
- **Dependencias**: Change #16, Change #18
- **Estimación**: 2 horas

---

### Change #20: `catalog-product-ingredientes-association`

- **Historias**: US-017
- **Funcionalidad**: Asociar ingredientes a productos (M2M) con flag removible
- **Backend**:
  - Tabla pivote: ProductoIngrediente (con es_removible)
  - Router: PUT `/api/v1/productos/:id/ingredientes`
  - Service: validar que ingredientes existan
- **Validaciones**: RN-CA07
- **Testing**: Un producto con múltiples ingredientes, algunos alergenos ✓
- **Dependencias**: Change #17, Change #18
- **Estimación**: 2 horas

---

### Change #21: `catalog-products-public-listing`

- **Historias**: US-018, US-019
- **Funcionalidad**: Endpoints públicos de listado y detalle (sin autenticación)
- **Backend**:
  - Router: GET `/api/v1/productos` (paginado, con filtros)
  - Router: GET `/api/v1/productos/:id` (detalle completo)
  - Filtros: categoría, nombre, rango de precio, disponible
  - Devuelve solo disponible=true, eliminado_en IS NULL
- **Validaciones**: RN-CA08, RN-DA07
- **Testing**:
  - Listado paginado ✓
  - Filtro por categoría ✓
  - Búsqueda por nombre (ILIKE) ✓
  - Detalle con ingredientes y alergenos ✓
- **Dependencias**: Change #19, Change #20
- **Estimación**: 3 horas

---

### Change #22: `catalog-allergen-filtering`

- **Historias**: US-023
- **Funcionalidad**: Filtrar productos por alergenos a excluir
- **Backend**:
  - Query param: `?excluirAlergenos=1,3,7`
  - NOT EXISTS subquery en repositorio
- **Testing**: Excluir alergeno → producto no aparece ✓
- **Dependencias**: Change #21
- **Estimación**: 1-2 horas

---

### Change #23: `frontend-catalog-grid`

- **Historias**: US-018, US-019, US-023
- **Funcionalidad**: Página de catálogo con grid, filtros, búsqueda y paginación
- **Frontend**:
  - `pages/CatalogPage.tsx`
  - `features/catalog/ProductGrid.tsx`: grid con skeleton loaders
  - `features/catalog/ProductCard.tsx`: tarjeta individual
  - `features/catalog/FilterBar.tsx`: filtros por categoría, precio, alérgenos
  - Usar TanStack Query para fetching y caché
- **Testing**:
  - Grid renderiza productos ✓
  - Filtros funcionan ✓
  - Paginación funciona ✓
  - Debounce en búsqueda ✓
- **Dependencias**: Change #21, Change #22
- **Estimación**: 5-6 horas

---

### Change #24: `frontend-product-detail-modal`

- **Historias**: US-019
- **Funcionalidad**: Modal detalle de producto con ingredientes y botón "Agregar al carrito"
- **Frontend**:
  - `features/catalog/ProductDetailModal.tsx`
  - Mostrar ingredientes con badges de alérgenos
  - Botón "Agregar al carrito"
- **Testing**: Modal abre, muestra datos correctos, botón agrega al carrito ✓
- **Dependencias**: Change #23
- **Estimación**: 2-3 horas

---

## SPRINT 3: Dirección de Entrega

### Change #25: `addresses-crud`

- **Historias**: US-024, US-025, US-026, US-027, US-028
- **Funcionalidad**: CRUD de direcciones de entrega por usuario
- **Backend**:
  - Router: POST/PUT/GET/DELETE `/api/v1/direcciones`
  - Service: validar que user solo acceda a sus propias direcciones
  - DireccionRepository: listar_por_usuario()
  - PATCH `/api/v1/direcciones/:id/principal` para marcar como predeterminada
- **Validaciones**: RN-DI01, RN-DI02, RN-DI03, RN-RB05
- **Testing**:
  - Usuario solo ve sus direcciones ✓
  - Una dirección principal a la vez ✓
  - Primera dirección es principal automáticamente ✓
  - Soft delete ✓
- **Dependencias**: Change #12 (RBAC)
- **Estimación**: 3-4 horas

---

### Change #26: `frontend-addresses-ui`

- **Historias**: US-024, US-025, US-026, US-027
- **Funcionalidad**: Página de direcciones con CRUD
- **Frontend**:
  - `pages/AddressesPage.tsx`
  - `features/addresses/AddressList.tsx`
  - `features/addresses/AddressForm.tsx` (crear/editar)
  - `features/addresses/AddressModal.tsx`
- **Testing**: CRUD funciona, seleccionar dirección principal ✓
- **Dependencias**: Change #25
- **Estimación**: 4-5 horas

---

## SPRINT 4: Carrito y Gestión del Estado Cliente

### Change #27: `cart-store-persistence`

- **Historias**: US-029, US-030, US-034
- **Funcionalidad**: Carrito persistente en localStorage con personalización (exclusión de ingredientes)
- **Frontend**:
  - Ya existe cartStore (Change #6), aquí refinamos:
  - Acciones: addItem(), removeItem(), updateQuantity(), personalizar()
  - Selectores: totalItems(), subtotal(), totalPrice()
  - Persistencia completa en localStorage
- **Validaciones**: RN-CR01, RN-CR02, RN-CR03, RN-CR04, RN-CR05
- **Testing**:
  - Agregar producto al carrito ✓
  - Cerrar navegador → carrito persiste ✓
  - Mismo producto 2 veces → cantidad incrementa ✓
  - Personalización (excluir ingrediente) ✓
- **Dependencias**: Change #6
- **Estimación**: 2-3 horas

---

### Change #28: `frontend-cart-ui-drawer`

- **Historias**: US-029, US-031, US-032, US-033, US-034
- **Funcionalidad**: Drawer/sidebar del carrito con resumen y botón checkout
- **Frontend**:
  - `features/cart/CartDrawer.tsx`
  - `features/cart/CartItem.tsx`: línea del carrito
  - `features/cart/CartSummary.tsx`: total, costos
  - Botón "Ir al Checkout"
- **Testing**: Drawer abre, muestra items, botón checkout funciona ✓
- **Dependencias**: Change #27
- **Estimación**: 3-4 horas

---

## SPRINT 5: Pedidos (Dominio Central)

### Change #29: `orders-fsm-state-machine`

- **Historias**: US-035, US-039, US-040, US-041, US-042, US-043, US-044
- **Funcionalidad**: Máquina de estados del pedido (PENDIENTE → CONFIRMADO → EN_PREP → EN_CAMINO → ENTREGADO)
- **Backend**:
  - Tabla EstadoPedido (ya en seed)
  - Service: validar transiciones FSM
  - Mapa de transiciones permitidas:
    - PENDIENTE → CONFIRMADO (automática en pago aprobado)
    - CONFIRMADO → EN_PREP (por PEDIDOS/ADMIN)
    - EN_PREP → EN_CAMINO (por PEDIDOS/ADMIN)
    - EN_CAMINO → ENTREGADO (por PEDIDOS/ADMIN)
    - PENDIENTE/CONFIRMADO/EN_PREP → CANCELADO (con restricciones por rol)
  - HistorialEstadoPedido append-only (solo INSERT)
- **Validaciones**: RN-FS01-RN-FS09
- **Testing**:
  - No se permite salto (PENDIENTE → EN_PREP) → error ✓
  - No se permite retroceso ✓
  - Estados terminales no permiten transiciones ✓
- **Dependencias**: Change #3 (modelos en BD)
- **Estimación**: 3-4 horas

---

### Change #30: `orders-creation-atomic-uow`

- **Historias**: US-035, US-036, US-037, US-038
- **Funcionalidad**: Crear pedido de forma atómica con Unit of Work (validaciones, snapshots, stock)
- **Backend**:
  - Router: POST `/api/v1/pedidos` (solo CLIENT)
  - Service.crear_pedido():
    1. Validar usuario y dirección
    2. Validar forma de pago
    3. Validar productos disponibles y stock suficiente (SELECT FOR UPDATE)
    4. Calcular snapshots de precio y nombre
    5. Calcular snapshots de dirección
    6. Crear Pedido en estado PENDIENTE
    7. Crear DetallePedido por cada item con snapshots
    8. Crear HistorialEstadoPedido inicial (estado_desde=NULL)
  - TODO dentro de contexto UoW: si algo falla → ROLLBACK
- **Validaciones**: RN-PE01-RN-PE08
- **Testing**:
  - Stock insuficiente → no se crea nada ✓
  - Snapshots se guardan ✓
  - Historial registra creación ✓
  - Transacción atómica ✓
- **Dependencias**: Change #5 (UoW), Change #29 (FSM)
- **Estimación**: 5-6 horas (complejo)

---

### Change #31: `orders-stock-decrement-confirm`

- **Historias**: US-039
- **Funcionalidad**: Decrementar stock al confirmar pedido (PENDIENTE → CONFIRMADO)
- **Backend**:
  - Service: avanzar_estado() detecta PENDIENTE → CONFIRMADO
  - Decrementa stock atomicamente por cada producto
  - Si decremento falla en alguno → ROLLBACK de TODA la operación
- **Validaciones**: RN-FS03, RN-FS04
- **Testing**:
  - Confirmar pedido → stock decrementado ✓
  - Stock insuficiente en segundo producto → ROLLBACK, stock no cambia ✓
- **Dependencias**: Change #30
- **Estimación**: 2-3 horas

---

### Change #32: `orders-stock-restore-cancel`

- **Historias**: US-043
- **Funcionalidad**: Restaurar stock al cancelar un pedido confirmado
- **Backend**:
  - Service: avanzar_estado() detecta → CANCELADO
  - Si pedido estaba en CONFIRMADO o EN_PREP: restaura stock
  - Operación inversa a RN-FS03
- **Validaciones**: RN-FS05, RN-RB08 (solo ADMIN desde EN_PREP)
- **Testing**:
  - Cancelar pedido confirmado → stock restaurado ✓
  - Cancelar desde EN_PREP sin ser ADMIN → 403 ✓
- **Dependencias**: Change #31
- **Estimación**: 2 horas

---

### Change #33: `orders-list-and-detail-endpoints`

- **Historias**: US-018 (en contexto de pedidos), US-049, US-050, US-051
- **Funcionalidad**: Endpoints para listar y ver detalle de pedidos (con restricciones por rol)
- **Backend**:
  - Router: GET `/api/v1/pedidos` (paginado, filtro por estado)
    - CLIENT: solo sus pedidos
    - PEDIDOS/ADMIN: todos
  - Router: GET `/api/v1/pedidos/:id` (detalle completo)
    - Propietario o ADMIN/PEDIDOS
  - Incluir: items con snapshots, historial ordenado, pagos asociados
- **Validaciones**: RN-RB05, RN-DA07
- **Testing**:
  - CLIENT ve solo sus pedidos ✓
  - ADMIN ve todos ✓
  - Detalle incluye historial y pagos ✓
- **Dependencias**: Change #29, Change #30
- **Estimación**: 3-4 horas

---

### Change #34: `orders-state-transitions-endpoints`

- **Historias**: US-040, US-041, US-042, US-043, US-044
- **Funcionalidad**: Endpoints para avanzar estado y cancelar pedido
- **Backend**:
  - Router: PATCH `/api/v1/pedidos/:id/estado` (body: {nuevo_estado, motivo})
  - Router: PATCH `/api/v1/pedidos/:id/cancelar` (body: {motivo})
  - Service valida transiciones FSM y permisos por rol
  - Historial append-only registra cada transición
- **Validaciones**: RN-FS01-RN-FS09, RN-RB08
- **Testing**:
  - Avanzar estado válido ✓
  - Intento de salto → error ✓
  - Historial se actualiza ✓
- **Dependencias**: Change #29, Change #31, Change #32
- **Estimación**: 3-4 horas

---

### Change #35: `frontend-orders-list-page`

- **Historias**: US-049, US-050, US-051
- **Funcionalidad**: Página de pedidos con listado paginado y filtros
- **Frontend**:
  - `pages/OrdersPage.tsx`
  - `features/orders/OrdersList.tsx`: tabla/grid paginado
  - Filtro por estado
  - Columnas: ID, fecha, estado, total, acciones
- **Testing**: Listado paginado, filtros funcionan ✓
- **Dependencias**: Change #33
- **Estimación**: 3-4 horas

---

### Change #36: `frontend-order-detail-page`

- **Historias**: US-050
- **Funcionalidad**: Página de detalle de pedido con historial completo
- **Frontend**:
  - `pages/OrderDetailPage.tsx`
  - `features/orders/OrderDetail.tsx`: información completa
  - `features/orders/OrderItemsList.tsx`: líneas del pedido
  - `features/orders/OrderTimeline.tsx`: historial de estados con timestamps
  - `features/orders/PaymentStatus.tsx`: estado del pago
- **Testing**: Detalle completo visible, timeline muestra transiciones ✓
- **Dependencias**: Change #35
- **Estimación**: 4-5 horas

---

## SPRINT 6: Pagos (MercadoPago)

### Change #37: `payments-mercadopago-integration`

- **Historias**: US-045, US-046, US-047, US-048
- **Funcionalidad**: Integración con MercadoPago Checkout API (crear pago, webhook IPN)
- **Backend**:
  - Router: POST `/api/v1/pagos/crear` (crear orden en MP)
  - Router: POST `/api/v1/pagos/webhook` (endpoint IPN)
  - Service: crear preferencia en MP, generar idempotency_key
  - Webhook: recibe notificación, valida firma, obtiene estado real del pago, actualiza tabla Pago
  - Si pago approved: avanza pedido a CONFIRMADO automáticamente (RN-PA05)
  - Tabla Pago con campos: mp_payment_id, mp_status, external_reference, idempotency_key
- **Validaciones**: RN-PA01-RN-PA09
- **Testing**:
  - Crear pago crea registro en tabla Pago ✓
  - Idempotency_key es único ✓
  - Webhook aprobado → pedido va a CONFIRMADO ✓
  - Webhook rechazado → pedido se queda en PENDIENTE ✓
- **Dependencias**: Change #30 (crear pedido)
- **Estimación**: 6-8 horas (integraciones externas)

---

### Change #38: `payments-multiple-attempts-per-order`

- **Historias**: US-048
- **Funcionalidad**: Un pedido puede tener múltiples intentos de pago (relación 1:N)
- **Backend**:
  - Tabla Pago ya soporta esto (1:N con Pedido)
  - Router: GET `/api/v1/pagos/pedido/:id` para ver historial de intentos
- **Testing**: Múltiples intentos visibles ✓
- **Dependencias**: Change #37
- **Estimación**: 1 hora

---

### Change #39: `frontend-checkout-card-payment`

- **Historias**: US-045, US-046, US-047
- **Funcionalidad**: Página de checkout con formulario de tarjeta (SDK MercadoPago)
- **Frontend**:
  - `pages/CheckoutPage.tsx`
  - `features/checkout/CheckoutForm.tsx`: direcciones, resumen, botón pagar
  - `features/checkout/CardPayment.tsx`: formulario tarjeta con @mercadopago/sdk-react
  - Flujo: seleccionar dirección → revisar items → ingresar tarjeta → crear pago
- **Testing**:
  - Tarjeta sandbox aprobada → pago creado ✓
  - Tarjeta sandbox rechazada → error mostrado ✓
- **Dependencias**: Change #25 (direcciones), Change #27 (carrito), Change #37 (pagos)
- **Estimación**: 5-6 horas

---

### Change #40: `frontend-payment-status-polling`

- **Historias**: US-046, US-047
- **Funcionalidad**: Polling de estado de pago (cada 2-3 segundos)
- **Frontend**:
  - `features/checkout/PaymentPolling.tsx`: hook que hace polling
  - Mostrar: pendiente, aprobado, rechazado
  - Si aprobado → redirigir a página de éxito
  - Si rechazado → mostrar error + botón reintentar
- **Testing**: Polling detecta cambio de estado ✓
- **Dependencias**: Change #39
- **Estimación**: 2-3 horas

---

## SPRINT 7: Perfil de Usuario

### Change #41: `profile-user-view-and-edit`

- **Historias**: US-061, US-062, US-063
- **Funcionalidad**: Ver y editar perfil del cliente
- **Backend**:
  - Router: GET `/api/v1/perfil` (usuario autenticado)
  - Router: PUT `/api/v1/perfil` (actualizar nombre, email, teléfono, contraseña)
  - Service: validar email único, hashear contraseña nueva
- **Testing**: Perfil muestra datos correctos, edición funciona ✓
- **Dependencias**: Change #12 (RBAC)
- **Estimación**: 2-3 horas

---

### Change #42: `frontend-profile-page`

- **Historias**: US-061, US-062, US-063
- **Funcionalidad**: Página de perfil con CRUD
- **Frontend**:
  - `pages/ProfilePage.tsx`
  - `features/profile/ProfileForm.tsx`
  - `features/profile/ChangePasswordForm.tsx`
- **Testing**: Ediciones persisten ✓
- **Dependencias**: Change #41
- **Estimación**: 2-3 horas

---

## SPRINT 8: Panel de Administración

### Change #43: `admin-dashboard-metrics`

- **Historias**: US-052, US-065
- **Funcionalidad**: Dashboard con métricas KPI (recharts)
- **Backend**:
  - Router: GET `/api/v1/admin/metricas` (solo ADMIN)
  - Service: calcular: total de pedidos, ventas totales, productos populares, estado de pedidos
  - Respuesta: datos para gráficos
- **Frontend**:
  - `pages/AdminDashboard.tsx`
  - `features/admin/MetricsCards.tsx`: cards con KPIs
  - `features/admin/SalesChart.tsx`: gráfico de ventas por fecha
  - `features/admin/OrderStatusChart.tsx`: gráfico de estados
  - `features/admin/TopProductsChart.tsx`: productos más vendidos
  - Usar recharts
- **Testing**: Dashboard carga, gráficos renderizan datos ✓
- **Dependencias**: Change #12 (RBAC), Change #30 (pedidos)
- **Estimación**: 4-5 horas

---

### Change #44: `admin-users-management`

- **Historias**: US-054
- **Funcionalidad**: CRUD de usuarios y asignación de roles
- **Backend**:
  - Router: GET/POST/PUT/DELETE `/api/v1/admin/usuarios`
  - Service: validar que solo ADMIN hace operaciones
- **Frontend**:
  - `pages/AdminUsersPage.tsx`
  - `features/admin/UsersList.tsx`: tabla de usuarios
  - `features/admin/UserForm.tsx`: crear/editar usuario
  - `features/admin/RoleAssignment.tsx`: selector de roles
- **Testing**: CRUD funciona, roles asignados correctamente ✓
- **Dependencias**: Change #12 (RBAC)
- **Estimación**: 4-5 horas

---

### Change #45: `admin-products-management`

- **Historias**: US-055, US-056, US-057, US-064
- **Funcionalidad**: CRUD de productos desde el panel (con relaciones)
- **Backend**: Ya existe en Change #18, Change #19, Change #20
- **Frontend**:
  - `pages/AdminProductsPage.tsx`
  - `features/admin/ProductsList.tsx`: tabla paginada
  - `features/admin/ProductForm.tsx`: crear/editar
  - `features/admin/CategorySelector.tsx`: multi-select categorías
  - `features/admin/IngredientSelector.tsx`: multi-select ingredientes
  - Soft delete: checkbox para mostrar eliminados
- **Testing**: Crear/editar/eliminar producto, relaciones asignadas ✓
- **Dependencies**: Change #18, Change #19, Change #20
- **Estimación**: 5-6 horas

---

### Change #46: `admin-categories-management`

- **Historias**: US-058, US-059
- **Funcionalidad**: CRUD de categorías desde el panel
- **Backend**: Ya existe en Change #16
- **Frontend**:
  - `pages/AdminCategoriesPage.tsx`
  - `features/admin/CategoriesList.tsx`: árbol jerárquico
  - `features/admin/CategoryForm.tsx`: crear/editar
  - Parent selector con validación de ciclos
- **Testing**: Crear/editar categoría, árbol se actualiza ✓
- **Dependencias**: Change #16
- **Estimación**: 3-4 horas

---

### Change #47: `admin-stock-management`

- **Historias**: US-060
- **Funcionalidad**: Panel de gestión de stock (actualizar cantidades)
- **Backend**:
  - Router: PATCH `/api/v1/admin/productos/:id/stock` (solo ADMIN/STOCK)
- **Frontend**:
  - `pages/AdminStockPage.tsx`
  - `features/admin/StockTable.tsx`: tabla editable con cantidades
  - Edición inline: click en cantidad → input → Enter para guardar
- **Testing**: Editar cantidad, persiste correctamente ✓
- **Dependencies**: Change #18, Change #12 (RBAC)
- **Estimación**: 3 horas

---

### Change #48: `admin-orders-management-fsm`

- **Historias**: US-041, US-042, US-043
- **Funcionalidad**: Panel para gestionar pedidos (ver listado, avanzar estados, cancelar)
- **Frontend**:
  - `pages/AdminOrdersPage.tsx`
  - `features/admin/OrdersManagementList.tsx`: tabla de pedidos
  - `features/admin/OrderStateButtons.tsx`: botones para avanzar/cancelar estado
  - Modal para confirmar cambios con observación opcional
- **Testing**: Avanzar estado, cancelar pedido, historial se actualiza ✓
- **Dependencias**: Change #34 (endpoints)
- **Estimación**: 4-5 horas

---

## SPRINT 9: Refinamientos y Calidad

### Change #49: `error-handling-standardization`

- **Historias**: US-068, US-074
- **Funcionalidad**: Estandarizar manejo de errores (RFC 7807) y validación de inputs
- **Backend**:
  - Exception handlers globales en main.py
  - Todas las excepciones mapean a RFC 7807
  - Validación de inputs con Pydantic (ya existe), pero refinar
  - Sanitización contra XSS: escape de HTML entities en textos
- **Frontend**:
  - Error boundary global
  - Toast con mensajes amigables
- **Testing**: Error 400 muestra detalles, 403 muestra "Sin permisos" ✓
- **Dependencias**: Change #5 (UoW), todos los changes anteriores
- **Estimación**: 2-3 horas

---

### Change #50: `testing-and-documentation`

- **Historias**: Bonus testing
- **Funcionalidad**: Tests unitarios (pytest) y documentación
- **Backend**:
  - `tests/test_auth.py`: login, register, refresh, logout
  - `tests/test_pedidos.py`: crear pedido, avanzar estado, cancelar
  - `tests/test_pagos.py`: crear pago, webhook
  - Cobertura > 60%
- **Frontend**:
  - Documentación de componentes con Storybook (opcional)
  - README completo
- **Testing**: `pytest` corre, cobertura calculada ✓
- **Dependencias**: Todos los changes anteriores
- **Estimación**: 5-6 horas

---

## Resumen: Orden de Implementación

### Fase 0: Infraestructura (2-3 semanas)

1. `setup-monorepo-estructura` (Change #1)
2. `backend-setup-fastapi-dependencies` (Change #2)
3. `backend-setup-database-alembic-seed` (Change #3)
4. `frontend-setup-react-vite-dependencies` (Change #4)
5. `backend-patterns-infrastructure-base` (Change #5)
6. `frontend-zustand-stores-setup` (Change #6)
7. `frontend-axios-interceptors-setup` (Change #7)

**Parallelizable**: Changes 2 y 4 pueden correr en paralelo

### Fase 1: Autenticación (2-3 semanas)

8. `auth-user-registration` (Change #8)
9. `auth-user-login-rate-limiting` (Change #9)
10. `auth-token-refresh-rotation` (Change #10)
11. `auth-logout` (Change #11)
12. `auth-rbac-roles` (Change #12)
13. `frontend-auth-ui-forms` (Change #13)
14. `frontend-navigation-rbac` (Change #14)
15. `frontend-error-handling-global` (Change #15)

### Fase 2: Catálogo (3 semanas)

16. `catalog-categories-hierarchical` (Change #16)
17. `catalog-ingredients-allergens` (Change #17)
18. `catalog-products-crud` (Change #18)
19. `catalog-product-categorias-association` (Change #19)
20. `catalog-product-ingredientes-association` (Change #20)
21. `catalog-products-public-listing` (Change #21)
22. `catalog-allergen-filtering` (Change #22)
23. `frontend-catalog-grid` (Change #23)
24. `frontend-product-detail-modal` (Change #24)

### Fase 3: Direcciones (1 semana)

25. `addresses-crud` (Change #25)
26. `frontend-addresses-ui` (Change #26)

### Fase 4: Carrito (1 semana)

27. `cart-store-persistence` (Change #27)
28. `frontend-cart-ui-drawer` (Change #28)

### Fase 5: Pedidos (4 semanas) — **Núcleo del sistema**

29. `orders-fsm-state-machine` (Change #29)
30. `orders-creation-atomic-uow` (Change #30)
31. `orders-stock-decrement-confirm` (Change #31)
32. `orders-stock-restore-cancel` (Change #32)
33. `orders-list-and-detail-endpoints` (Change #33)
34. `orders-state-transitions-endpoints` (Change #34)
35. `frontend-orders-list-page` (Change #35)
36. `frontend-order-detail-page` (Change #36)

### Fase 6: Pagos MercadoPago (2-3 semanas)

37. `payments-mercadopago-integration` (Change #37)
38. `payments-multiple-attempts-per-order` (Change #38)
39. `frontend-checkout-card-payment` (Change #39)
40. `frontend-payment-status-polling` (Change #40)

### Fase 7: Perfil (1 semana)

41. `profile-user-view-and-edit` (Change #41)
42. `frontend-profile-page` (Change #42)

### Fase 8: Admin Panel (2-3 semanas)

43. `admin-dashboard-metrics` (Change #43)
44. `admin-users-management` (Change #44)
45. `admin-products-management` (Change #45)
46. `admin-categories-management` (Change #46)
47. `admin-stock-management` (Change #47)
48. `admin-orders-management-fsm` (Change #48)

### Fase 9: Refinamientos (1-2 semanas)

49. `error-handling-standardization` (Change #49)
50. `testing-and-documentation` (Change #50)

---

## Métricas Totales

- **Total de Changes**: 50
- **Duración estimada**: 12-15 semanas
- **Parallelizable**: 8 changes (infraestructura y admin)
- **Dependencias críticas**: Autenticación → Catálogo → Pedidos → Pagos

---

## Patrones Aplicados

| Change   | Patrón                                         |
| -------- | ---------------------------------------------- |
| #5       | Unit of Work, Repository, Layered Architecture |
| #29      | State Machine (FSM)                            |
| #30      | Snapshot Pattern, Atomic Transactions          |
| #33      | RBAC, Pagination                               |
| #37      | Webhook, Idempotency Keys                      |
| #23, #35 | Feature-Sliced Design, TanStack Query          |
| #27      | Zustand + localStorage persistence             |

---

## Próximos Pasos

1. **Revisar y ajustar este mapa**: ¿Faltan funcionalidades? ¿Hay dependencias incorrectas?
2. **Comenzar Phase 0**: `/opsx:propose setup-monorepo-estructura`
3. **Paralelizar**: mientras se implementa backend, frontend puede avanzar
4. **Sincronizar**: cada 2-3 changes, hacer merge a main y actualizar specs
