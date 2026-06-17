# logging-frontend Specification

## Purpose
TBD - created by archiving change implement-logging-and-monitoring. Update Purpose after archive.
## Requirements
### Requirement: devLogger MUST only output in development mode

El sistema DEBE emitir logs solo cuando `import.meta.env.DEV` es `true`. En producción, los logs NO DEBEN aparecer en la consola.

#### Scenario: Log in development mode is emitted

- **WHEN** la aplicación se ejecuta con `vite dev` y se llama a `devLogger.info("User logged in")`
- **THEN** aparece un mensaje en la consola del navegador con el prefijo `[FoodStore]`

#### Scenario: Log in production mode is suppressed

- **WHEN** la aplicación se ejecuta con `vite build && vite preview` y se llama a `devLogger.info("User logged in")`
- **THEN** NO aparece ningún mensaje en la consola del navegador

---

### Requirement: Log entries MUST include timestamp, level, and action

El sistema DEBE estructurar cada log entry con al menos los campos timestamp, level, y action.

#### Scenario: Info log entry has structured format

- **WHEN** se llama a `devLogger.info("Cart updated", { items: 3 })`
- **THEN** el segundo argumento de `console.log` es un objeto con `timestamp` (ISO string), `level: "info"`, `action: "Cart updated"`, `data: { items: 3 }`

#### Scenario: Error log entry has structured format

- **WHEN** se llama a `devLogger.error("Payment failed", { error: "timeout" })`
- **THEN** el segundo argumento de `console.error` es un objeto con `timestamp`, `level: "error"`, `action: "Payment failed"`, `data: { error: "timeout" }`

#### Scenario: Log without data omits data field from console output

- **WHEN** se llama a `devLogger.info("User logged out")` sin pasar data
- **THEN** solo se pasa el string `"[FoodStore] User logged out"` a `console.log` (sin segundo argumento)

---

### Requirement: Log levels MUST map to correct console methods

El sistema DEBE usar `console.error` para level `error`, `console.warn` para level `warn`, y `console.log` para levels `info` y `debug`.

#### Scenario: Error level uses console.error

- **WHEN** se llama a `devLogger.error("Crash", data)`
- **THEN** se invoca `console.error(...)`

#### Scenario: Warn level uses console.warn

- **WHEN** se llama a `devLogger.warn("Deprecated", data)`
- **THEN** se invoca `console.warn(...)`

#### Scenario: Info level uses console.log

- **WHEN** se llama a `devLogger.info("Ready", data)`
- **THEN** se invoca `console.log(...)`

#### Scenario: Debug level uses console.log

- **WHEN** se llama a `devLogger.debug("Refreshing token", data)`
- **THEN** se invoca `console.log(...)`

---

### Requirement: Auth actions MUST be logged

El sistema DEBE loguear las acciones de autenticación: login exitoso, logout, y refresh de token.

#### Scenario: Login success is logged

- **WHEN** un usuario inicia sesión exitosamente
- **THEN** se llama a `devLogger.info` con una acción que indica login

#### Scenario: Logout is logged

- **WHEN** un usuario cierra sesión
- **THEN** se llama a `devLogger.info` con una acción que indica logout

#### Scenario: Token refresh is logged at debug level

- **WHEN** el sistema refresca el token JWT automáticamente
- **THEN** se llama a `devLogger.debug` con una acción que indica refresh

---

### Requirement: Cart actions MUST be logged

El sistema DEBE loguear las acciones del carrito: agregar ítem, remover ítem, y vaciar carrito.

#### Scenario: Add to cart is logged

- **WHEN** un usuario agrega un producto al carrito
- **THEN** se llama a `devLogger.info` con una acción que indica agregar al carrito y datos del producto

#### Scenario: Remove from cart is logged

- **WHEN** un usuario remueve un producto del carrito
- **THEN** se llama a `devLogger.info` con una acción que indica remover del carrito

#### Scenario: Clear cart is logged

- **WHEN** un usuario vacía el carrito
- **THEN** se llama a `devLogger.info` con una acción que indica vaciar carrito

---

### Requirement: Payment flow MUST be logged

El sistema DEBE loguear los eventos del flujo de pago: inicio, éxito, y fallo.

#### Scenario: Payment initiation is logged

- **WHEN** un usuario inicia el proceso de pago
- **THEN** se llama a `devLogger.info` con una acción que indica inicio de pago

#### Scenario: Payment success is logged

- **WHEN** un pago se completa exitosamente
- **THEN** se llama a `devLogger.info` con una acción que indica pago exitoso

#### Scenario: Payment failure is logged

- **WHEN** un pago falla
- **THEN** se llama a `devLogger.error` con una acción que indica fallo de pago y datos del error

---

### Requirement: Order state changes MUST be logged in admin

El sistema DEBE loguear los cambios de estado de pedidos desde el panel de administración.

#### Scenario: Admin changes order state

- **WHEN** un administrador cambia el estado de un pedido (ej: de "pendiente" a "confirmado")
- **THEN** se llama a `devLogger.info` con una acción que indica el cambio de estado y el nuevo estado

---

### Requirement: ErrorBoundary errors MUST be logged with structured data

El sistema DEBE loguear los errores capturados por el ErrorBoundary con datos estructurados.

#### Scenario: ErrorBoundary catches an error

- **WHEN** un componente renderiza un error y el ErrorBoundary lo captura
- **THEN** se llama a `console.error` con datos estructurados que incluyen el mensaje de error y el componente donde ocurrió

---

### Requirement: API requests MUST be logged in dev mode via axios interceptor

El sistema DEBE loguear todas las requests HTTP en modo desarrollo a través del interceptor de respuesta de axios.

#### Scenario: Successful API request is logged at debug level

- **WHEN** se hace una request `GET /api/v1/productos` que retorna 200 en modo desarrollo
- **THEN** se llama a `devLogger.debug` con el método HTTP, la URL, y el status code

#### Scenario: API request logging is suppressed in production

- **WHEN** se hace una request en modo producción
- **THEN** NO se llama a `devLogger.debug` para la request

---

### Requirement: TanStack Query DevTools MUST be available in development builds

El sistema DEBE renderizar el componente `ReactQueryDevtools` solo cuando la aplicación se ejecuta en modo desarrollo.

#### Scenario: DevTools render in development

- **WHEN** la aplicación se ejecuta con `vite dev`
- **THEN** el componente `ReactQueryDevtools` está presente en el DOM

#### Scenario: DevTools do not render in production

- **WHEN** la aplicación se ejecuta con `vite build && vite preview`
- **THEN** el componente `ReactQueryDevtools` NO está presente en el DOM

