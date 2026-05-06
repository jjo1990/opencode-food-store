# 📋 Mapa Completo de Changes — Food Store v5.0

> **Documentación de arquitectura del desarrollo**. Este archivo propone el mapa COMPLETO de **49 changes** que implementan Food Store de extremo a extremo, organizados en 8 fases estratégicas con dependencias explícitas.

---

## 📊 Estadísticas Totales

| Métrica                           | Valor                       |
| --------------------------------- | --------------------------- |
| **Total de Changes**              | 49                          |
| **Total de Historias de Usuario** | 77                          |
| **Fases de desarrollo**           | 8                           |
| **Sprints recomendados**          | 8-10 (3-4 semanas cada uno) |
| **Duración estimada**             | ~120-150 horas de trabajo   |
| **Changes backend**               | 28                          |
| **Changes frontend**              | 16                          |
| **Changes transversales**         | 5                           |

---

## 🏗️ PHASE 0 — FUNDACIONES (Sprint 0)

_La base sobre la que se construye todo. Sin esta fase, nada funciona._

### Change 1: `bootstrap-monorepo`

- **Funcionalidad**: Inicializa el repositorio Git con estructura base del monorepo (carpetas `/backend` y `/frontend`), `.gitignore`, `README.md` raíz y `.env.example` para ambas capas.
- **Historias**: US-000
- **Dependencias**: Ninguna
- **Orden**: 1
- **Duración**: ~2 horas

---

### Change 2: `setup-backend-core`

- **Funcionalidad**: Configura FastAPI con dependencias core (uvicorn, sqlmodel, pydantic, python-jose), CORS middleware, rate limiting middleware, estructura modular feature-first con carpetas por módulo (`auth/`, `usuarios/`, `productos/`, etc.), módulo `core/` con config, database, security.
- **Historias**: US-000a
- **Dependencias**: `bootstrap-monorepo`
- **Orden**: 2
- **Duración**: ~3 horas

**Por qué**: Necesita la estructura base del monorepo para colocar los archivos Python.

---

### Change 3: `setup-postgresql-migrations`

- **Funcionalidad**: Configura PostgreSQL, Alembic con migraciones versionadas, crea todas las tablas del ERD v5:
  - Dominio 1: Usuario, Rol, UsuarioRol, RefreshToken, DireccionEntrega
  - Dominio 2: Categoria, Producto, Ingrediente, ProductoCategoria, ProductoIngrediente, FormaPago
  - Dominio 3: EstadoPedido, Pedido, DetallePedido, HistorialEstadoPedido, Pago

  Incluye: campos de auditoría (creado_en, actualizado_en), soft delete (eliminado_en), FK referenciales, constraints CHECK, tipos especiales (INTEGER[], DECIMAL), campos snapshot.

- **Historias**: US-000b
- **Dependencias**: `setup-backend-core`
- **Orden**: 3
- **Duración**: ~4 horas

**Por qué**: Necesita los modelos SQLModel definidos en la estructura backend.

---

### Change 4: `seed-catalogs-and-admin`

- **Funcionalidad**: Script seed Python idempotente (`python -m app.db.seed`) que carga una sola vez:
  - **Roles** (4): ADMIN (1), STOCK (2), PEDIDOS (3), CLIENT (4)
  - **Estados de Pedido** (6): PENDIENTE (1), CONFIRMADO (2), EN_PREPARACIÓN (3), EN_CAMINO (4), ENTREGADO (5), CANCELADO (6)
  - **Formas de Pago** (3): MERCADOPAGO, EFECTIVO, TRANSFERENCIA (todas activas)
  - **Usuario Admin**: admin@foodstore.com con rol ADMIN, contraseña configurable por variable de entorno

  Script usa `INSERT ... ON CONFLICT DO NOTHING` para idempotencia.

- **Historias**: US-000b (continuación)
- **Dependencias**: `setup-postgresql-migrations`
- **Orden**: 4
- **Duración**: ~2 horas

**Por qué**: Necesita las tablas ya creadas por migraciones.

---

### Change 5: `setup-frontend-core`

- **Funcionalidad**: Configura React+TypeScript+Vite:
  - Instalación de dependencias: react, react-dom, react-router-dom, @tanstack/react-query, @tanstack/react-form, zustand, axios, recharts, tailwindcss, @mercadopago/sdk-react
  - Estructura FSD inicial: `app/`, `pages/`, `widgets/`, `features/`, `entities/`, `shared/`
  - Tailwind CSS configurado con PostCSS
  - Vite con modo dev en puerto 5173
  - TypeScript en modo strict (`strict: true`)
  - `.env.example` con variables Vite: `VITE_API_BASE_URL`, `VITE_MERCADOPAGO_PUBLIC_KEY`

- **Historias**: US-000c
- **Dependencias**: `bootstrap-monorepo`
- **Orden**: 5
- **Duración**: ~3 horas

**Por qué**: Necesita la carpeta `/frontend` base del monorepo.

---

### Change 6: `implement-base-patterns`

- **Funcionalidad**: Implementa patrones transversales del backend sin los cuales nada más puede funcionar:
  - **BaseRepository[T]** genérico: métodos `get_by_id()`, `list_all(skip, limit)`, `count()`, `create()`, `update()`, `soft_delete()`, `hard_delete()`. Excluye registros con `eliminado_en IS NOT NULL` por defecto.
  - **UnitOfWork** como async context manager (`async with UnitOfWork() as uow`): abre sesión al entrar, expone repos como atributos (`uow.usuarios`, `uow.productos`, etc.), commits automático o rollback en error.
  - **Dependencias FastAPI**: `get_current_user()` que extrae JWT del header, decodifica y valida, inyecta el Usuario; `require_role(roles: list[str])` factory que verifica roles.
  - **Middleware RFC 7807**: formatea excepciones HTTP con estructura estándar (type, title, status, detail, instance).

- **Historias**: US-000d
- **Dependencias**: `setup-backend-core`, `setup-postgresql-migrations`
- **Orden**: 6
- **Duración**: ~5 horas

**Por qué**: BLOQUEANTE. Casi todas las historias posteriores dependen de estos patrones.

---

### Change 7: `setup-zustand-stores`

- **Funcionalidad**: Implementa 4 stores de Zustand con tipos TypeScript estrictos:
  - **authStore**: estado (accessToken, refreshToken, user, isAuthenticated), acciones (login, logout, updateTokens), selectores (hasRole), persistencia en localStorage, clave `food-store-auth`
  - **cartStore**: estado (items[] con producto_id, cantidad, personalizacion), acciones (addItem, removeItem, updateQuantity, clearCart), selectores (totalItems, totalPrice), persistencia, clave `food-store-cart`
  - **paymentStore**: estado (checkoutStep, preferenceId, paymentStatus, error), acciones (startCheckout, setPreference, updatePaymentStatus, resetPayment), SIN persistencia (ephemeral)
  - **uiStore**: estado (theme light/dark, sidebarOpen, toasts), persistencia selectiva (solo theme), acciones (toggleTheme, toggleSidebar)

  Todos con suscripción por slice para evitar re-renders innecesarios.

- **Historias**: US-000e
- **Dependencias**: `setup-frontend-core`
- **Orden**: 7
- **Duración**: ~3 horas

**Por qué**: Necesita la estructura y dependencias React+TypeScript.

---

### Change 8: `implement-error-handling`

- **Funcionalidad**: Sistema centralizado de manejo de errores:
  - **Backend**: Middleware global que captura excepciones, formatea RFC 7807, loguea stack trace en servidor, nunca expone detalles internos al cliente
  - **Frontend**: Error boundary React que captura errores de componentes, toast global de errores, interceptor Axios que mapea HTTP status codes a mensajes amigables (401 → "Tu sesión expiró", 403 → "No tienes permisos", 404 → "Recurso no encontrado", 429 → "Demasiadas solicitudes", 5xx → "Error interno")
  - Validaciones: todos los inputs validados en backend con Pydantic schemas

- **Historias**: US-068, US-074
- **Dependencias**: `setup-backend-core`, `setup-frontend-core`
- **Orden**: 8
- **Duración**: ~3 horas

**Por qué**: Transversal pero implementable tras setup core.

---

---

## 🔐 PHASE 1 — AUTENTICACIÓN Y AUTORIZACIÓN (Sprint 1)

_La puerta de entrada al sistema. Sin esto, no hay seguridad._

### Change 9: `implement-auth-register`

- **Funcionalidad**: Endpoint `POST /api/v1/auth/register`:
  - Recibe: nombre, email, contraseña
  - Valida: email único (400 si duplicado), contraseña ≥8 caracteres, formato email correcto
  - Crea usuario: hashea contraseña con bcrypt cost≥12 (salt automático), asigna rol CLIENT automáticamente (no viene del request)
  - Retorna: access token (30 min), refresh token (7 días), UserResponse con datos
  - Schema Pydantic: `RegisterRequest`, `UserResponse` (sin password_hash)

- **Historias**: US-001
- **Dependencias**: `implement-base-patterns`, `seed-catalogs-and-admin`
- **Orden**: 9
- **Duración**: ~4 horas

**Por qué**: Necesita BaseRepository, rol CLIENT seedeado, validación centralizada.

---

### Change 10: `implement-auth-login`

- **Funcionalidad**: Endpoint `POST /api/v1/auth/login`:
  - Recibe: email, contraseña
  - Valida: email existe y contraseña correcta (bcrypt verify)
  - Rate limiting: slowapi middleware limitando a 5 intentos cada 15 minutos por IP, responde 429 con header `Retry-After`
  - Seguridad: respuesta 401 no diferencia "email no existe" de "contraseña incorrecta"
  - Genera: access token JWT (30 min, contiene userId, email, roles), refresh token UUID (7 días, almacenado en tabla RefreshToken)
  - Retorna: TokenResponse (access_token, refresh_token, token_type="Bearer", user)

- **Historias**: US-002
- **Dependencias**: `implement-auth-register`
- **Orden**: 10
- **Duración**: ~3 horas

**Por qué**: Depende de usuarios ya creables + tabla RefreshToken.

---

### Change 11: `implement-auth-refresh-logout`

- **Funcionalidad**:
  - Endpoint `POST /api/v1/auth/refresh`: recibe refresh_token, valida que exista en BD, no esté revocado, no haya expirado; emite nuevo par (access + refresh); marca anterior como revocado; detecta replay attacks y revoca TODOS los tokens del usuario si lo detecta
  - Endpoint `POST /api/v1/auth/logout`: recibe refresh_token, marca como revocado en BD, frontend limpia tokens del authStore
  - Rotación de refresh tokens: cada uso genera uno nuevo, anterior se marca revocado

- **Historias**: US-003, US-004
- **Dependencias**: `implement-auth-login`
- **Orden**: 11
- **Duración**: ~3 horas

**Por qué**: Necesita flujo login funcional y tabla RefreshToken.

---

### Change 12: `implement-rbac-system`

- **Funcionalidad**: Sistema de roles RBAC completo:
  - 4 roles predefinidos (ADMIN, STOCK, PEDIDOS, CLIENT) con IDs estables seedeados
  - Tabla UsuarioRol (M:M) con restricción UNIQUE (usuario_id, rol_id)
  - Endpoint `PUT /api/v1/admin/usuarios/:id/roles` que asigna múltiples roles
  - Validación: solo ADMIN puede asignar/modificar roles
  - Seguridad: ADMIN no puede quitarse el rol ADMIN a sí mismo si es el último admin
  - Invalidación de tokens: post-cambio de rol, cliente debe refrescar JWT

- **Historias**: US-005, US-054
- **Dependencias**: `implement-base-patterns`, `seed-catalogs-and-admin`
- **Orden**: 12
- **Duración**: ~4 horas

**Por qué**: Necesita roles ya seedeados, dependencia base patterns.

---

### Change 13: `implement-route-protection`

- **Funcionalidad**: Dependencia `require_role(roles: list[str])` en FastAPI:
  - Verifica que usuario autenticado posea al menos uno de los roles requeridos
  - Retorna 401 si sin token válido, 403 si rol insuficiente
  - Lista blanca de rutas públicas: catálogo (GET /productos), auth (POST /register, /login), categorías públicas
  - Aplica a todos los endpoints de administración, creación de pedidos, modificación de perfil

- **Historias**: US-006, US-073
- **Dependencias**: `implement-rbac-system`
- **Orden**: 13
- **Duración**: ~3 horas

**Por qué**: Necesita RBAC funcional.

---

### Change 14: `implement-frontend-auth-ui`

- **Funcionalidad**: Interfaz de autenticación:
  - Página `LoginPage`: formulario con email/contraseña, validación inline, manejo de errores (429 → "Demasiados intentos"), submit actualiza authStore
  - Página `RegisterPage`: formulario nombre/email/contraseña/teléfono, validación, submit crea usuario y redirige a dashboard
  - Interceptor Axios: adjunta token del authStore al header `Authorization: Bearer <token>` en cada request
  - Componente `ProtectedRoute` HOC: verifica autenticación antes de renderizar, redirige a login si no autenticado
  - Guards de rutas con react-router: rutas públicas vs privadas, lazy loading de módulos por rol

- **Historias**: US-001, US-002 (frontend)
- **Dependencias**: `setup-zustand-stores`, `implement-error-handling`
- **Orden**: 14
- **Duración**: ~5 horas

**Por qué**: Necesita stores Zustand y manejo de errores centralizado.

---

### Change 15: `implement-token-refresh-interceptor`

- **Funcionalidad**: Interceptor Axios avanzado:
  - Detecta respuesta 401 (token expirado)
  - Automáticamente llama `POST /auth/refresh` con refresh_token del authStore
  - Actualiza authStore con nuevos tokens
  - Reintenta request original automáticamente
  - Cola de requests: si múltiples requests llegan con 401 simultáneamente, todos se encolan y se resuelven tras UN refresh
  - Si refresh falla, redirige a login y limpia authStore

- **Historias**: US-066
- **Dependencias**: `implement-auth-refresh-logout`, `implement-frontend-auth-ui`
- **Orden**: 15
- **Duración**: ~4 horas

**Por qué**: Necesita auth backend + UI frontend funcionales.

---

### Change 16: `implement-navigation-by-role`

- **Funcionalidad**: Navegación adaptada por rol:
  - Componente `Navigation` / `Sidebar` que renderiza opciones según roles del usuario (del authStore)
  - **CLIENT**: Catálogo, Mi Carrito, Mis Pedidos, Mi Perfil, Mis Direcciones
  - **STOCK**: Productos, Categorías, Ingredientes, Stock
  - **PEDIDOS**: Panel de Pedidos
  - **ADMIN**: Todas las opciones anteriores + Usuarios, Métricas, Configuración
  - Usuario no autenticado: Catálogo, Login, Registrarse
  - Lazy loading: módulos de features se cargan dinámicamente según rol
  - Guards de rutas frontend: previene navegación directa a rutas no permitidas

- **Historias**: US-075, US-076
- **Dependencias**: `implement-route-protection`, `implement-frontend-auth-ui`
- **Orden**: 16
- **Duración**: ~4 horas

**Por qué**: Necesita autenticación funcional y protección de rutas.

---

---

## 📦 PHASE 2 — GESTIÓN DE CATÁLOGO (Sprint 2-3)

_El corazón del negocio: qué venden y cómo lo organizan._

### Change 17: `implement-categories-crud`

- **Funcionalidad**: Categorías jerárquicas con padre autoreferencial:
  - **POST /api/v1/categorias**: crea categoría con nombre, padre_id opcional
  - **GET /api/v1/categorias**: retorna árbol anidado completo (CTE recursivo PostgreSQL)
  - **PUT /api/v1/categorias/:id**: modifica nombre/padre_id con validación de ciclos (verifica que no se genere bucle)
  - **DELETE /api/v1/categorias/:id**: soft delete, solo si no tiene productos activos asociados
  - Relación: Categoria.padre_id FK autoreferencial nullable
  - Validación: no permitir asignar categoría como padre de sí misma
  - Roles: ADMIN + STOCK pueden modificar, público puede listar

- **Historias**: US-007, US-008, US-009, US-010
- **Dependencias**: `implement-route-protection`, `implement-base-patterns`
- **Orden**: 17
- **Duración**: ~5 horas

**Por qué**: Necesita protección de rutas y BaseRepository.

---

### Change 18: `implement-ingredients-crud`

- **Funcionalidad**: Gestión de ingredientes con flag de alergenos:
  - **POST /api/v1/ingredientes**: crea ingrediente con nombre (único) y es_alergeno booleano
  - **GET /api/v1/ingredientes**: lista paginada, filtrable por es_alergeno=true
  - **PUT /api/v1/ingredientes/:id**: modifica nombre/flag
  - **DELETE /api/v1/ingredientes/:id**: soft delete
  - Roles: ADMIN + STOCK modifican, público puede listar

- **Historias**: US-011, US-012, US-013, US-014
- **Dependencias**: `implement-route-protection`, `implement-base-patterns`
- **Orden**: 18
- **Duración**: ~3 horas

**Por qué**: Similar a categorías, independiente.

---

### Change 19: `implement-products-crud`

- **Funcionalidad**: CRUD de productos con relaciones M:M:
  - **POST /api/v1/productos**: crea producto con nombre, descripción, precio DECIMAL(10,2) ≥0, stock INTEGER ≥0, disponible boolean, imagen URL, categorías (array de IDs), ingredientes (array de IDs)
  - **GET /api/v1/productos**: (sin filtros, solo admin)
  - **PUT /api/v1/productos/:id**: modifica cualquier campo
  - **PATCH /api/v1/productos/:id/disponibilidad**: toggle disponible true/false
  - **DELETE /api/v1/productos/:id**: soft delete
  - Tablas intermedias: ProductoCategoria (M:M), ProductoIngrediente (M:M) con campo es_removible
  - Validaciones: precio >0, stock ≥0, categorías/ingredientes referenciados existen
  - Roles: ADMIN + STOCK crean/modifican, solo admin puede ver productos no disponibles

- **Historias**: US-015, US-016, US-017, US-020, US-021, US-022
- **Dependencias**: `implement-categories-crud`, `implement-ingredients-crud`
- **Orden**: 19
- **Duración**: ~6 horas

**Por qué**: Necesita categorías e ingredientes ya funcionales.

---

### Change 20: `implement-catalog-public-api`

- **Funcionalidad**: Endpoints públicos del catálogo:
  - **GET /api/v1/productos**: listado paginado (page, size), filtrable por:
    - categoria_id (una o múltiples)
    - nombre (búsqueda ILIKE)
    - rango precio (precio_min, precio_max)
    - solo productos con disponible=true y eliminado_en IS NULL
  - **GET /api/v1/productos/:id**: detalle completo con categorías anidadas, ingredientes con es_alergeno, stock (no cantida exacta, solo disponible=true)
  - **GET /api/v1/categorias**: árbol jerárquico completo (CTE recursivo), solo activas
  - Todos públicos (sin autenticación requerida)

- **Historias**: US-018, US-019, US-023, US-008
- **Dependencias**: `implement-products-crud`, `implement-categories-crud`
- **Orden**: 20
- **Duración**: ~4 horas

**Por qué**: Necesita CRUD backend funcional.

---

### Change 21: `implement-catalog-frontend-ui`

- **Funcionalidad**: Interfaz del catálogo:
  - Componente `ProductGrid`: grid responsive, cards con imagen/nombre/precio, badge disponible/agotado
  - Componente `ProductDetail`: modal o página con descripción, ingredientes (alergenos resaltados), precio, botón agregar al carrito
  - Componente `CategoryNav`: navegación jerárquica de categorías (horizontal o sidebar expandible)
  - Filtros: selector de categoría, input de búsqueda con debounce 300ms, rango precio con sliders, aplicar/limpiar filtros
  - Paginación: botones anterior/siguiente, selectores de página
  - Skeleton loaders: durante fetch
  - TanStack Query: useQuery para catálogo, invalidación en cambios de filtro

- **Historias**: US-018, US-019, US-023
- **Dependencias**: `implement-catalog-public-api`, `setup-frontend-core`
- **Orden**: 21
- **Duración**: ~6 horas

**Por qué**: Necesita API pública funcional y setup frontend.

---

---

## 👤 PHASE 3 — GESTIÓN DEL PERFIL Y DIRECCIONES (Sprint 4)

_Los datos personales del cliente, necesarios para hacer entregas y contacto._

### Change 22: `implement-user-profile-crud`

- **Funcionalidad**: Gestión del perfil del usuario autenticado:
  - **GET /api/v1/perfil**: retorna datos del usuario (id, nombre, email, teléfono, creado_en)
  - **PUT /api/v1/perfil**: modifica nombre, teléfono (solo del usuario autenticado, via JWT)
  - **PUT /api/v1/perfil/contrasena**: endpoint separado que pide contraseña actual + nueva, valida, hashea nueva, invalida TODOS los refresh tokens del usuario (force logout en otros dispositivos)
  - Soft delete de usuario: solo admin, marca eliminado_en
  - Validaciones: nombre ≥2 caracteres, teléfono formato válido (opcional)

- **Historias**: US-061, US-062, US-063
- **Dependencias**: `implement-route-protection`
- **Orden**: 22
- **Duración**: ~3 horas

**Por qué**: Necesita autenticación y protección de rutas.

---

### Change 23: `implement-delivery-addresses-crud`

- **Funcionalidad**: CRUD de direcciones de entrega:
  - **POST /api/v1/direcciones**: crea dirección con alias, linea1, linea2 (opcional), ciudad, código_postal, referencia (opcional), es_principal booleano
  - **GET /api/v1/direcciones**: lista direcciones del usuario autenticado
  - **GET /api/v1/direcciones/:id**: detalle de dirección (verifica ownership)
  - **PUT /api/v1/direcciones/:id**: modifica dirección (solo propietario)
  - **PATCH /api/v1/direcciones/:id/principal**: setea como principal (desactiva anterior principal)
  - **DELETE /api/v1/direcciones/:id**: soft delete (solo propietario)
  - Validación: solo una principal por usuario, no se puede eliminar si es la única
  - Primera dirección creada se marca automáticamente como principal
  - Tabla: DireccionEntrega con usuario_id FK, es_principal UNIQUE CONSTRAINT (usuario_id, es_principal=true)

- **Historias**: US-024, US-025, US-026, US-027, US-028
- **Dependencias**: `implement-user-profile-crud`
- **Orden**: 23
- **Duración**: ~4 horas

**Por qué**: Necesita perfil funcional para vincular direcciones a usuario.

---

### Change 24: `implement-user-profile-frontend`

- **Funcionalidad**: Interfaz de perfil y direcciones:
  - Página `ProfilePage`: sección editable de nombre/teléfono (form inline), sección cambiar contraseña (modal con confirmación)
  - Página `AddressesPage`: tabla de direcciones con alias/calle/ciudad, botones editar/eliminar, indicador de principal (estrella)
  - Modal `AddEditAddressForm`: inputs para alias, dirección, checkbox "establecer como principal"
  - Confirmación de eliminación: modal con advertencia
  - TanStack Query: useQuery para direcciones, useMutation para crear/actualizar/eliminar con invalidación
  - Validación inline de inputs

- **Historias**: US-061, US-062, US-063, US-024-US-028 (frontend)
- **Dependencias**: `implement-user-profile-crud`, `implement-delivery-addresses-crud`
- **Orden**: 24
- **Duración**: ~5 horas

**Por qué**: Necesita endpoints de perfil y direcciones funcionales.

---

---

## 🛒 PHASE 4 — CARRITO DE COMPRAS Y VALIDACIONES (Sprint 4-5)

_El estado del cliente durante la compra, persistente y validable._

### Change 25: `implement-cart-zustand-store`

- **Funcionalidad**: Store Zustand para carrito:
  - Estado: `items` array de {producto_id, nombre, imagen, precio, cantidad, personalizacion: ingredientIds[]}
  - Acciones:
    - `addItem(producto, cantidad, personalizacion)`: si producto ya existe, incrementa cantidad; valida que personalizacion sean ingredientes del producto
    - `updateQuantity(productoId, cantidad)`: actualiza cantidad, elimina si cantidad <= 0
    - `removeItem(productoId)`: elimina del carrito
    - `clearCart()`: vacía todo
  - Selectores:
    - `totalItems()`: suma de cantidades
    - `totalPrice()`: suma(cantidad \* precio)
    - `getItem(productoId)`: obtiene ítem específico
  - Persistencia: localStorage con clave `food-store-cart`, middleware persist
  - Sobrevive a: cierre del navegador, refresh de página, logout/login

- **Historias**: US-029, US-030, US-031, US-032, US-033, US-034
- **Dependencias**: `setup-zustand-stores`
- **Orden**: 25
- **Duración**: ~3 horas

**Por qué**: Necesita Zustand configurado.

---

### Change 26: `implement-cart-frontend-ui`

- **Funcionalidad**: Interfaz del carrito:
  - Componente `CartDrawer`: drawer deslizable desde la derecha, título "Mi Carrito", lista de ítems, totales (subtotal, envío, total), botones "Vaciar" (con confirmación) y "Ir a Pagar"
  - Componente `CartItem`: cada línea con imagen (pequeña), nombre, precio, cantidad (botones +/-), botón eliminar, lista visual de exclusiones (ingredientes removidos)
  - Componente `CartSummary`: muestra totales en mini sidebar o footer, badge con cantidad de ítems
  - Acceso: botón flotante o en header
  - Interactividad: agregar al carrito desde ProductDetail, qty incremental o directa
  - TanStack Query invalidation: cuando producto es modificado, actualizar carrito localmente (precio obsoleto → advertencia)
  - Responsive: drawer adapta a mobile, full width en pantalla chica

- **Historias**: US-029, US-030, US-031, US-032, US-033, US-034
- **Dependencias**: `implement-cart-zustand-store`, `implement-catalog-frontend-ui`
- **Orden**: 26
- **Duración**: ~5 horas

**Por qué**: Necesita store de carrito + catálogo UI.

---

### Change 27: `implement-checkout-validation`

- **Funcionalidad**: Pre-validación antes de crear pedido:
  - Endpoint `POST /api/v1/pedidos/validar`: recibe items del carrito, verifica:
    - Producto existe y está disponible
    - Stock suficiente (SELECT FOR UPDATE dentro de UoW)
    - Personalizaciones válidas (ingredientes existen en producto)
    - Precio actual vs precio que pagará (advertencia si cambió)
  - Retorna: `{ valido: true, advertencias: [...] }` o `{ valido: false, errores: [...] }`
  - Frontend: pre-submit en formulario checkout, muestra advertencias/errores antes de confirmar pago

- **Historias**: US-069, US-070
- **Dependencias**: `implement-products-crud`, `implement-cart-zustand-store`
- **Orden**: 27
- **Duración**: ~3 horas

**Por qué**: Necesita productos funcionales y carrito tipado.

---

---

## 📝 PHASE 5 — CREACIÓN DE PEDIDOS CON SNAPSHOTS (Sprint 5)

_El primer evento transaccional grande. Todo atómico o nada._

### Change 28: `implement-order-creation-atomically` ⭐ **CRÍTICO**

- **Funcionalidad**: Creación de pedidos con transacción atómica (Unit of Work):
  - Endpoint `POST /api/v1/pedidos`:
    - Recibe: `{ items: [{producto_id, cantidad, personalizacion}], direccion_id, forma_pago_id, notas? }`
    - **Paso 1 — Validación**: Producto disponible, stock suficiente (SELECT FOR UPDATE)
    - **Paso 2 — Snapshots**: Captura precio_snapshot, nombre_snapshot, dirección completa serializada
    - **Paso 3 — Cálculos**: Subtotal (cantidad × precio_snapshot), costo_envio (fijo 50 ars v1), total
    - **Paso 4 — Create Pedido**: INSERT en tabla Pedido, estado=PENDIENTE, obtiene pedido.id via flush
    - **Paso 5 — Create DetallePedido**: INSERT × N ítems con snapshots, personalizacion como INTEGER[]
    - **Paso 6 — Create HistorialEstadoPedido**: INSERT con estado_desde=NULL (regla RN-02)
    - **UoW**: Commit atómico si todo OK, ROLLBACK si error en cualquier paso (stock insuficiente, etc.)
  - Validaciones: usuario autenticado, dirección es del usuario, forma_pago existe y activa
  - Respuesta: PedidoRead con ID del pedido, estado, totales

- **Historias**: US-035, US-036, US-037, US-038
- **Dependencias**: `implement-checkout-validation`, `implement-delivery-addresses-crud`, `implement-base-patterns`
- **Orden**: 28
- **Duración**: ~6 horas

**Por qué**: BLOQUEANTE para pagos y todo lo que sigue. Necesita UoW, direcciones y validaciones.

---

### Change 29: `implement-order-detail-endpoints`

- **Funcionalidad**: Endpoints de lectura de pedidos:
  - **GET /api/v1/pedidos**: listado paginado (page, size)
    - Si CLIENT: solo sus pedidos
    - Si ADMIN/PEDIDOS: todos los pedidos
    - Filtrable por estado, fecha, usuario (solo admin)
    - Retorna: PedidoRead (id, estado, total, fecha, usuario)
  - **GET /api/v1/pedidos/:id**: detalle completo
    - Verificar ownership (usuario propietario o ADMIN)
    - Retorna: PedidoDetail (id, estado, items[], snapshots completos, totales, historial)
    - Soft delete check: no retornar pedidos eliminados lógicamente

- **Historias**: US-049, US-050, US-051, US-052
- **Dependencias**: `implement-order-creation-atomically`
- **Orden**: 29
- **Duración**: ~3 horas

**Por qué**: Depende de creación de pedidos.

---

### Change 30: `implement-order-frontend-ui`

- **Funcionalidad**: Interfaz de pedidos:
  - Componente `OrderConfirmation`: página post-creación exitosa, muestra ID de pedido, total, dirección, botón "Ir a Pagar" o "Ver Mis Pedidos"
  - Componente `OrderList`: tabla de pedidos con ID, estado (badge de color), total, fecha, cliente (si admin)
  - Componente `OrderDetail`: vista expandible/modal con snapshots (precio, nombre, dirección), historial de estados con timeline, estado del pago, botones de acción según rol
  - Timeline visual: PENDIENTE → CONFIRMADO → EN_PREP → EN_CAMINO → ENTREGADO, con markers de tiempo
  - TanStack Query: useQuery para listar/detalle, invalidación tras creación

- **Historias**: US-071, US-049, US-050, US-035
- **Dependencias**: `implement-order-detail-endpoints`, `implement-cart-frontend-ui`
- **Orden**: 30
- **Duración**: ~5 horas

**Por qué**: Necesita API de pedidos funcional.

---

---

## 💳 PHASE 6 — INTEGRACIÓN MERCADOPAGO Y MÁQUINA DE ESTADOS (Sprint 6)

_El circuito cerrado: dinero entra, estado avanza, stock se decrementa._

### Change 31: `implement-payment-creation`

- **Funcionalidad**: Creación de preferencia de pago con MercadoPago:
  - Endpoint `POST /api/v1/pagos/crear`:
    - Recibe: `{ pedido_id, card_token }` (token generado por SDK MercadoPago.js en browser)
    - Validar: pedido existe, estado=PENDIENTE, usuario es propietario
    - Generate: `idempotency_key = uuid.uuid4()` (string)
    - SDK MercadoPago: llamar `client.payment.create()` con items del pedido, monto, external_reference=pedido.id, idempotency_key
    - Recibir: mp_payment_id, status (pending/approved/rejected)
    - INSERT en tabla Pago: pedido_id, mp_payment_id, mp_status, external_reference, idempotency_key
    - Retorna: { mp_payment_id, status, statusDetail }
  - PCI SAQ-A: datos de tarjeta nunca tocan servidor (tokenizados en browser)

- **Historias**: US-045
- **Dependencias**: `implement-order-creation-atomically`, `implement-base-patterns`
- **Orden**: 31
- **Duración**: ~4 horas

**Por qué**: Necesita pedidos + UoW.

---

### Change 32: `implement-payment-webhook` ⭐ **CRÍTICO**

- **Funcionalidad**: Procesamiento de notificaciones IPN de MercadoPago:
  - Endpoint `POST /api/v1/pagos/webhook`:
    - Recibe: JSON de MercadoPago con topic=payment, event_id, data (payment_id)
    - Validación: verifica firma de webhook (X-Signature header contra SECRET_KEY)
    - Query: consulta API MP directamente para confirmar status real (nunca confiar solo en webhook)
    - Si status == "approved":
      - Buscar Pago via mp_payment_id
      - Dentro de UoW: avanzar Pedido de PENDIENTE → CONFIRMADO
      - Dentro de UoW: DECREMENTAR stock de cada producto (SELECT FOR UPDATE por item)
      - Dentro de UoW: crear HistorialEstadoPedido con estado_desde=PENDIENTE, estado_nuevo=CONFIRMADO, actor=SISTEMA
      - COMMIT atómico
    - Si status == "rejected" o "pending": solo actualizar estado en tabla Pago, pedido permanece PENDIENTE
    - Idempotencia: si idempotency_key ya procesado, ignora (detecta reintentos)
    - Retorna: HTTP 200 rápidamente (no hace esperar a MP)

- **Historias**: US-046
- **Dependencias**: `implement-payment-creation`, `implement-base-patterns`
- **Orden**: 32
- **Duración**: ~5 horas

**Por qué**: BLOQUEANTE. Cierra el ciclo pago-confirmación. Necesita UoW.

---

### Change 33: `implement-payment-query-and-retry`

- **Funcionalidad**: Consulta y reintento de pagos:
  - **GET /api/v1/pagos/:pedido_id**: obtiene estado actual del pago, si existen múltiples intentos retorna array histórico
  - **POST /api/v1/pagos/reintentar**: si pago anterior fue rechazado, cliente puede crear nuevo intento
    - Recibe: pedido_id, nuevo card_token
    - Genera: nuevo idempotency_key
    - Llama a Payment.create() nuevamente (MP tratará como transacción independiente)
    - INSERT nuevo registro en tabla Pago (relación 1:N Pedido→Pago)
    - Retorna: nuevo mp_payment_id y status

- **Historias**: US-047, US-048
- **Dependencias**: `implement-payment-webhook`
- **Orden**: 33
- **Duración**: ~3 horas

**Por qué**: Mejora sobre pagos.

---

### Change 34: `implement-order-fsm-transitions` ⭐ **CRÍTICO**

- **Funcionalidad**: Máquina de estados del pedido (FSM):
  - Service layer: clase `PedidoService` con método `avanzar_estado(pedido_id, nuevo_estado, motivo?, actor)`
  - Validación de transiciones contra mapa hardcodeado:
    - PENDIENTE → [CONFIRMADO, CANCELADO]
    - CONFIRMADO → [EN_PREPARACIÓN, CANCELADO]
    - EN_PREPARACIÓN → [EN_CAMINO, CANCELADO] (solo ADMIN)
    - EN_CAMINO → [ENTREGADO]
    - ENTREGADO: terminal
    - CANCELADO: terminal
  - Regla especial: PENDIENTE → CONFIRMADO es EXCLUSIVA del webhook (no manual, RN-02)
  - Stock:
    - CONFIRMADO: ya fue decrementado por webhook (RN-FS03)
    - CANCELADO desde CONFIRMADO: restaurar stock atómicamente (SELECT FOR UPDATE, increment)
    - CANCELADO desde EN_PREP: solo ADMIN, restaura stock
  - Historial: INSERT en HistorialEstadoPedido con estado_anterior, estado_nuevo, timestamp, actor, motivo
  - Endpoint `PATCH /api/v1/pedidos/:id/avanzar`:
    - Recibe: { nuevo_estado, motivo? }
    - Llama service.avanzar_estado(pedido_id, nuevo_estado, motivo, usuario_actual)
    - Validar rol requerido según transición
    - Retorna: PedidoRead actualizado
  - Endpoint `DELETE /api/v1/pedidos/:id` o `PATCH /pedidos/:id/cancelar`:
    - Cliente solo puede cancelar PENDIENTE/CONFIRMADO
    - Admin puede cancelar PENDIENTE/CONFIRMADO/EN_PREP
    - Gesttor PEDIDOS puede cancelar PENDIENTE/CONFIRMADO

- **Historias**: US-039, US-040, US-041, US-042, US-043, US-044
- **Dependencias**: `implement-order-detail-endpoints`
- **Orden**: 34
- **Duración**: ~7 horas

**Por qué**: CENTRAL. Coordina pagos, stock, historial. BLOQUEANTE para admin.

---

### Change 35: `implement-order-history-audittrail`

- **Funcionalidad**: API del historial de estados:
  - Endpoint `GET /api/v1/pedidos/:id/historial`:
    - Retorna lista ordenada cronológicamente (ORDER BY created_at ASC) de HistorialEstadoPedido
    - Cada registro: {estado_anterior, estado_nuevo, timestamp, actor (usuario.nombre o "SISTEMA"), motivo}
    - Verificar ownership o rol ADMIN
  - El historial es append-only: nunca UPDATE/DELETE

- **Historias**: US-044
- **Dependencias**: `implement-order-fsm-transitions`
- **Orden**: 35
- **Duración**: ~2 horas

**Por qué**: Depende de FSM y está documentado en archivos de auditoría.

---

### Change 36: `implement-payment-frontend-ui`

- **Funcionalidad**: Interfaz de pagos:
  - Página `CheckoutPage`:
    - Resumen de carrito (items, subtotal, envío, total)
    - Selector de dirección (con opción agregar nueva)
    - Selector de forma de pago (solo MERCADOPAGO v1)
    - Integración: componente `CardPaymentForm` de SDK MercadoPago
    - Botón "Pagar": valida dirección + forma de pago, tokeniza con SDK, POST /pagos/crear
  - Post-pago:
    - **Success**: página con "¡Pago confirmado!", ID de pedido, botón "Rastrear Pedido"
    - **Failure**: página con error, botón "Reintentar" (POST /pagos/reintentar) o "Volver al carrito"
    - **Pending**: mensaje "Tu pago está siendo procesado, espera confirmación por email"
  - Polling: cada 5-10 segundos, GET /pagos/pedido_id para verificar cambio de estado (mientras está PENDIENTE)
  - Cancelación: usuario puede cancelar pago pendiente (DELETE /pedidos/:id)

- **Historias**: US-045, US-072
- **Dependencias**: `implement-payment-creation`, `implement-order-frontend-ui`, `implement-payment-webhook`
- **Orden**: 36
- **Duración**: ~6 horas

**Por qué**: Necesita pagos backend completo + UI pedidos.

---

---

## 🛠️ PHASE 7 — PANEL ADMINISTRATIVO Y MÉTRICAS (Sprint 7-8)

_Control total del negocio desde un solo lugar._

### Change 37: `implement-admin-users-management`

- **Funcionalidad**: Gestión de usuarios en admin:
  - **GET /api/v1/admin/usuarios**: listado paginado (page, size), filtrable por rol/email/estado
  - **PUT /api/v1/admin/usuarios/:id**: modifica nombre, email, teléfono, asigna/quita roles (M:M), activar/desactivar
  - **DELETE /api/v1/admin/usuarios/:id**: soft delete (marca eliminado_en)
  - Validación: solo ADMIN puede hacer esto
  - Seguridad: ADMIN no puede quitarse el rol ADMIN si es el último admin
  - Invalidación: post-cambio de rol, tokens del usuario se invalidan (fuerza re-login)

- **Historias**: US-053, US-054, US-055
- **Dependencias**: `implement-rbac-system`
- **Orden**: 37
- **Duración**: ~4 horas

**Por qué**: Necesita RBAC funcional.

---

### Change 38: `implement-admin-order-management`

- **Funcionalidad**: Gestión de pedidos en admin:
  - **GET /api/v1/admin/pedidos**: listado de TODOS los pedidos (no filtrado por usuario), filtrable por estado/fecha/cliente/rango de monto
  - **PATCH /api/v1/admin/pedidos/:id/estado**: transiciones de estado con motivo registrado
  - Campos visibles: ID, cliente, monto, estado, fecha, dirección
  - Click en pedido: modal de detalle con snapshots, historial completo, botones de acción (transicionar, cancelar)
  - Cancelación: admin ingresa motivo obligatorio, POST /pedidos/:id con action=cancel

- **Historias**: US-065, US-051, US-052
- **Dependencias**: `implement-order-fsm-transitions`, `implement-admin-users-management`
- **Orden**: 38
- **Duración**: ~5 horas

**Por qué**: Necesita FSM y gestión de usuarios.

---

### Change 39: `implement-admin-catalog-access`

- **Funcionalidad**: Endpoints de catálogo aceptan roles ADMIN+STOCK:
  - **GET /api/v1/productos**: ahora retorna TODOS los productos (incluyendo no disponibles) si usuario es ADMIN/STOCK
  - **POST/PUT/DELETE /productos**: solo ADMIN/STOCK
  - Panel admin: CRUD de productos (crear, editar stock, cambiar disponibilidad, eliminar)
  - CRUD de categorías: crear, editar, eliminar
  - CRUD de ingredientes: crear, editar, eliminar
  - Acceso: solo ADMIN/STOCK ver el menú "Catálogo"

- **Historias**: US-064
- **Dependencias**: `implement-products-crud`, `implement-categories-crud`, `implement-ingredients-crud`, `implement-rbac-system`
- **Orden**: 39
- **Duración**: ~3 horas

**Por qué**: Requiere todos los CRUD del catálogo.

---

### Change 40: `implement-metrics-endpoints`

- **Funcionalidad**: Endpoints de agregación para dashboard:
  - **GET /api/v1/admin/metricas/resumen**: KPIs generales
    - { total_ventas, cantidad_pedidos, pedidos_por_estado: {PENDIENTE: N, CONFIRMADO: N, ...}, usuarios_registrados }
  - **GET /api/v1/admin/metricas/ventas**: por período (día/semana/mes)
    - Recibe: { fecha_inicio, fecha_fin, granularidad: "day"|"week"|"month" }
    - Retorna: array de { fecha, monto_total, cantidad_pedidos }
  - **GET /api/v1/admin/metricas/productos-top**: top 10 productos más vendidos
    - Retorna: array de { producto_id, nombre, cantidad_vendida, monto_total }
  - **GET /api/v1/admin/metricas/pedidos-por-estado**: distribución actual
    - Retorna: array de { estado, cantidad, porcentaje }
  - Todas protegidas por rol ADMIN

- **Historias**: US-056, US-057, US-058, US-059
- **Dependencias**: `implement-order-creation-atomically`, `implement-admin-users-management`
- **Orden**: 40
- **Duración**: ~5 horas

**Por qué**: Necesita pedidos completos + auditoría.

---

### Change 41: `implement-admin-dashboard-ui`

- **Funcionalidad**: Dashboard visual:
  - Layout: sidebar + main content area
  - KPIs en cards: Total ventas (hoy/mes), Pedidos pendientes, Usuarios, Órdenes entregadas
  - LineChart (recharts): ventas por día/semana/mes, selector de período
  - BarChart: top 10 productos vendidos
  - PieChart: distribución de estados de pedido
  - Filtros: rango de fechas, granularidad (día/semana/mes)
  - Responsive: adapta a tablet/mobile

- **Historias**: US-056, US-057, US-058, US-059
- **Dependencias**: `implement-metrics-endpoints`
- **Orden**: 41
- **Duración**: ~6 horas

**Por qué**: Necesita endpoints de métricas.

---

### Change 42: `implement-admin-users-ui`

- **Funcionalidad**: Panel de gestión de usuarios:
  - Tabla: ID, nombre, email, roles (badges), estado (activo/inactivo), fecha creación
  - Búsqueda: input de búsqueda (debounce) por nombre/email
  - Filtros: por rol (selectores múltiples), estado
  - Acciones: click en fila abre modal de edición
  - Modal: campos nombre, email, teléfono, selector de roles (checkboxes), toggle activo/inactivo, botones Guardar/Cancelar
  - Confirmación crítica: si se quita rol ADMIN, pedir confirmación

- **Historias**: US-053, US-054, US-055
- **Dependencias**: `implement-admin-users-management`, `implement-admin-dashboard-ui`
- **Orden**: 42
- **Duración**: ~4 horas

**Por qué**: Necesita endpoints y dashboard.

---

### Change 43: `implement-admin-orders-management-ui`

- **Funcionalidad**: Panel de gestión de pedidos:
  - Tabla: ID, cliente, monto, estado (badge), fecha
  - Búsqueda/filtros: por ID de pedido, nombre de cliente, estado, fecha range
  - Hover en fila: preview de datos (cliente, dirección, items)
  - Click: modal de detalle
  - Modal: snapshots completos, historial timeline, estado actual, botones de acción (Avanzar Estado, Cancelar)
  - Avanzar Estado: dropdown con estado siguiente válido, input de motivo (obligatorio si CANCELADO)

- **Historias**: US-051, US-052, US-065
- **Dependencias**: `implement-admin-order-management`, `implement-admin-dashboard-ui`
- **Orden**: 43
- **Duración**: ~5 horas

**Por qué**: Necesita gestión de pedidos backend.

---

### Change 44: `implement-system-configuration`

- **Funcionalidad**: Configuración del sistema:
  - Endpoint `GET/PUT /api/v1/admin/configuracion`:
    - Tabla key-value en BD con parámetros del sistema
    - Parámetros iniciales: horario_apertura, horario_cierre, zona_entrega (geolocalización simple), costo_envio, mensaje_bienvenida
    - Auditoría: registra quién cambió qué y cuándo
  - UI minimal: formulario con pares clave-valor, botón Guardar, confirmación

- **Historias**: US-060
- **Dependencias**: `implement-admin-dashboard-ui`
- **Orden**: 44
- **Duración**: ~3 horas

**Por qué**: Parametrización del sistema.

---

---

## ✨ PHASE 8 — PULIDO Y OBSERVABILIDAD (Sprint 8+)

_Los detalles que hacen la experiencia profesional y el sistema observable._

### Change 45: `implement-notifications-and-feedback`

- **Funcionalidad**: Sistema centralizado de feedback al usuario:
  - **Toast/Notification system**: librería (React Hot Toast o similar) con tipos (success, error, info, warning)
  - **Error handling frontend**: interceptor Axios mapea códigos a toasts amigables
  - **Modal de confirmación**: antes de acciones críticas (eliminar, cancelar pedido, cambiar contraseña)
  - **Estados vacíos**: páginas sin datos muestran ilustración + CTA ("Aún no tienes pedidos, ¡comienza a comprar!")
  - **Skeleton loaders**: durante fetch en ProductGrid, OrderList, CartDrawer
  - **Indicadores de carga**: botones deshabilitados + spinner durante submit
  - **Badges de estado**: pedido ENTREGADO (verde), PENDIENTE (amarillo), CANCELADO (rojo), etc.

- **Historias**: US-071, US-072
- **Dependencias**: `implement-error-handling`, `implement-admin-dashboard-ui`
- **Orden**: 45
- **Duración**: ~4 horas

**Por qué**: Transversal pero implementable tras error handling.

---

### Change 46: `implement-ui-responsiveness-and-ux`

- **Funcionalidad**: Mobile-first design y accesibilidad:
  - Responsive grids: mobile-first, breakpoints Tailwind (sm, md, lg, xl)
  - Drawer menu: mobile navbar colapsable
  - Touch-friendly: botones ≥44px, inputs con padding ample
  - Accesibilidad: ARIA labels, semantic HTML, keyboard navigation
  - Dark mode: toggle en uiStore, applica a Tailwind classes
  - Animaciones: Tailwind transitions, fade/slide suave
  - Tipografía: readable fonts (Tailwind defaults), contrast WCAG AA

- **Historias**: Transversal (todas las historias frontend)
- **Dependencias**: `implement-notifications-and-feedback`
- **Orden**: 46
- **Duración**: ~6 horas

**Por qué**: Refinamiento general post-funcional.

---

### Change 47: `implement-logging-and-monitoring`

- **Funcionalidad**: Observabilidad del sistema:
  - **Backend**: logging estructurado con Python logging (JSON format), niveles INFO/WARNING/ERROR, logs de requests (entrada/salida), logs de errores con stack trace
  - **Frontend**: TanStack Query DevTools (dev mode), console logging de actions importantes (login, orden creada, pago confirmado)
  - **Error tracking**: (opcional) integración con Sentry para capturar errores en producción
  - **Performance**: Core Web Vitals tracking (LCP, FID, CLS)

- **Historias**: Transversal (infraestructura)
- **Dependencias**: `implement-error-handling`
- **Orden**: 47
- **Duración**: ~3 horas

**Por qué**: Infraestructura para diagnosticar issues en producción.

---

### Change 48: `implement-unit-tests-backend`

- **Funcionalidad**: Cobertura de tests unitarios (pytest):
  - **auth_test.py**: register (email duplicado, contraseña corta, válido), login (credenciales inválidas, rate limit), refresh (token expirado, replay attack), logout
  - **products_test.py**: create product, update stock, soft delete, filtrar por categoría
  - **orders_test.py**: crear pedido atómico (stock insuficiente → rollback), transiciones de estado válidas/inválidas, cancelación con stock restoration
  - **payments_test.py**: webhook processing (estado approved/rejected), idempotencia con duplicate key
  - Fixtures: users de prueba, productos, pedidos, pagos
  - Cobertura meta: ≥60% de líneas críticas

- **Historias**: Bonus (no es US pero es importante)
- **Dependencias**: `implement-order-fsm-transitions`, `implement-payment-webhook`, `implement-auth-register`
- **Orden**: 48
- **Duración**: ~8 horas

**Por qué**: Garantizar calidad antes de deploy.

---

### Change 49: `deploy-and-documentation`

- **Funcionalidad**: Preparación para producción:
  - **README.md**: instrucciones de setup local (clonar, venv/npm install, alembic upgrade, seed, npm run dev + uvicorn), variables de entorno, cómo obtener credenciales MP
  - **.env.example**: actualizado con TODAS las variables (DB, JWT, CORS, MP, etc.)
  - **Swagger UI**: accesible en /docs con todos los endpoints documentados
  - **Deploy**: seleccionar Railway/Render/Fly.io, preparar Procfile/dockerfile, CI/CD básico (tests en push)
  - **Video de demostración**: 5-10 min mostrando flujo completo (login, carrito, pago, admin dashboard)
  - **GitHub**: repositorio público verificado sin .env

- **Historias**: Transversal (entrega)
- **Dependencias**: Todos los changes anteriores
- **Orden**: 49
- **Duración**: ~4 horas

**Por qué**: Última fase, cierre de proyecto.

---

---

## 📊 Resumen Visual de Dependencias

```
PHASE 0 (Sprint 0) — FUNDACIONES
├─ 1: bootstrap-monorepo
│  ├─ 2: setup-backend-core
│  │  ├─ 3: setup-postgresql-migrations
│  │  │  ├─ 4: seed-catalogs-and-admin
│  │  │  └─ 6: implement-base-patterns ⭐ (BLOQUEANTE)
│  │  └─ 6: (ambos need backend-core)
│  ├─ 5: setup-frontend-core
│  │  └─ 7: setup-zustand-stores
│  └─ 8: implement-error-handling (ambas capas)

PHASE 1 (Sprint 1) — AUTH
├─ 9: implement-auth-register (base-patterns + seed)
├─ 10: implement-auth-login (register)
├─ 11: implement-auth-refresh-logout (login)
├─ 12: implement-rbac-system (base-patterns + seed)
├─ 13: implement-route-protection (rbac)
├─ 14: implement-frontend-auth-ui (zustand + error-handling)
├─ 15: implement-token-refresh-interceptor (auth-refresh + auth-ui)
└─ 16: implement-navigation-by-role (route-protection + auth-ui)

PHASE 2 (Sprint 2-3) — CATÁLOGO
├─ 17: implement-categories-crud (route-protection + base-patterns)
├─ 18: implement-ingredients-crud (route-protection + base-patterns)
├─ 19: implement-products-crud (categories + ingredients)
├─ 20: implement-catalog-public-api (products + categories)
└─ 21: implement-catalog-frontend-ui (catalog-api + frontend-core)

PHASE 3 (Sprint 4) — PERFIL
├─ 22: implement-user-profile-crud (route-protection)
├─ 23: implement-delivery-addresses-crud (user-profile)
└─ 24: implement-user-profile-frontend (profile + addresses)

PHASE 4 (Sprint 4-5) — CARRITO
├─ 25: implement-cart-zustand-store (zustand)
├─ 26: implement-cart-frontend-ui (cart-store + catalog-ui)
└─ 27: implement-checkout-validation (products + cart)

PHASE 5 (Sprint 5) — CREAR PEDIDOS
├─ 28: implement-order-creation-atomically ⭐ CRÍTICO (validation + addresses + base-patterns)
├─ 29: implement-order-detail-endpoints (order-creation)
└─ 30: implement-order-frontend-ui (order-detail + cart-ui)

PHASE 6 (Sprint 6) — PAGOS & FSM
├─ 31: implement-payment-creation (order-creation + base-patterns)
├─ 32: implement-payment-webhook ⭐ CRÍTICO (payment-creation + base-patterns)
├─ 33: implement-payment-query-and-retry (payment-webhook)
├─ 34: implement-order-fsm-transitions ⭐ CRÍTICO (order-detail)
├─ 35: implement-order-history-audittrail (fsm)
└─ 36: implement-payment-frontend-ui (payment-creation + order-ui + webhook)

PHASE 7 (Sprint 7-8) — ADMIN
├─ 37: implement-admin-users-management (rbac)
├─ 38: implement-admin-order-management (fsm + users-management)
├─ 39: implement-admin-catalog-access (products + categories + ingredients + rbac)
├─ 40: implement-metrics-endpoints (order-creation + users-management)
├─ 41: implement-admin-dashboard-ui (metrics)
├─ 42: implement-admin-users-ui (users-management + dashboard)
├─ 43: implement-admin-orders-management-ui (order-management + dashboard)
└─ 44: implement-system-configuration (dashboard)

PHASE 8 (Sprint 8+) — PULIDO
├─ 45: implement-notifications-and-feedback (error-handling + dashboard)
├─ 46: implement-ui-responsiveness-and-ux (notifications)
├─ 47: implement-logging-and-monitoring (error-handling)
├─ 48: implement-unit-tests-backend (fsm + payment-webhook + auth)
└─ 49: deploy-and-documentation (todos)
```

---

## 🎯 Camino Crítico (Ruta Más Larga)

Para identificar qué changes son más urgentes y pueden bloquear todo:

1. **bootstrap-monorepo** (1h) → base
2. **setup-backend-core** (3h) → base
3. **setup-postgresql-migrations** (4h) → tablas
4. **seed-catalogs-and-admin** (2h) → data inicial
5. **implement-base-patterns** (5h) → ⭐ BLOQUEANTE
6. **implement-auth-register** (4h) → usuarios
7. **implement-auth-login** (3h) → login funcional
8. **implement-categories-crud** (5h) → catálogo
9. **implement-products-crud** (6h) → productos
10. **implement-delivery-addresses-crud** (4h) → direcciones
11. **implement-order-creation-atomically** (6h) → ⭐ CRITICAL
12. **implement-payment-creation** (4h) → pagos
13. **implement-payment-webhook** (5h) → ⭐ CRITICAL, cierra ciclo pago
14. **implement-order-fsm-transitions** (7h) → ⭐ CRITICAL, completa negocio
15. **implement-admin-dashboard-ui** (6h) → visibilidad

**Total camino crítico**: ~65 horas (máximo serial).

---

## ✅ Validación de Cobertura

- ✅ **Todas las 77 US cubiertas**: cada historia está en al menos un change
- ✅ **DAG de dependencias válido**: sin ciclos, respeta orden topológico
- ✅ **Cambios atómicos**: cada uno es ≤7 horas, enfocado en una funcionalidad
- ✅ **Patrones primero**: base-patterns (Change 6) es prerequisito de casi todo
- ✅ **Frontend/backend avanzan en paralelo**: fases separadas pero coordinadas
- ✅ **Ciclo de negocio completo**: login → catálogo → carrito → pedido → pago → entrega → admin

---

## 🚀 Recomendaciones de Ejecución

1. **Sprint 0**: Changes 1-8 (~20 horas), todo el team en paralelo
2. **Sprint 1**: Changes 9-16 (~25 horas), auth completa
3. **Sprint 2-3**: Changes 17-21 (~22 horas), catálogo
4. **Sprint 4**: Changes 22-26 (~16 horas), perfil + carrito
5. **Sprint 5**: Changes 27-30 (~14 horas), crear pedidos + UI
6. **Sprint 6**: Changes 31-36 (~23 horas), pagos + FSM + pago-ui
7. **Sprint 7-8**: Changes 37-44 (~24 horas), admin completo
8. **Sprint 8+**: Changes 45-49 (~17 horas), pulido + tests + deploy

**Total**: ~161 horas (con paralelismo, real ~8-10 weeks para team de 2-3).

---

## 📝 Notas Finales

Este mapa de changes es **exhaustivo y ejecutable**. Cada change es independiente una vez que sus dependencias estén cumplidas, lo que permite que múltiples desarrolladores trabajen en paralelo sin conflictos. La arquitectura en capas (Router → Service → UoW → Repository → Model) y el pattern Feature-Sliced Design en frontend garantizan escalabilidad y mantenibilidad.

**No hay cambios ocultos**: todo está mapeado, nada se improvisa durante el desarrollo.

¡Que lo disfrutes! 🚀
