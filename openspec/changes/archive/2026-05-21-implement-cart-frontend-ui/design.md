## Context

El frontend tiene:

- `cartStore` con items persistentes en localStorage (Change 25 ✅)
- `ProductDetail` con botón "Agregar al carrito" placeholder (no funcional)
- `Header` con navegación y user info, sin entrada de carrito
- Shared components: Button, Card, Skeleton, EmptyState, ErrorDisplay
- Layout responsivo con Tailwind CSS

El carrito es estado 100% cliente — no necesita llamadas API para funcionar.

## Goals / Non-Goals

**Goals:**

- Drawer deslizable desde la derecha con lista de items del carrito
- Controles de cantidad (+/-) con actualización instantánea
- Botón eliminar item con feedback visual
- Badge en el header con cantidad total de items
- Desglose de totales (subtotal, envío, total)
- Botón "Vaciar carrito" con confirmación
- Botón "Ir a pagar" (placeholder, redirige a /checkout cuando exista)
- Botón "Agregar al carrito" funcional en ProductDetail
- Drawer responsivo

**Non-Goals:**

- Página de checkout (Change 27+)
- Validación de stock en frontend (se hace en backend)
- Sincronización con el servidor

## Decisions

### 1. CartDrawer como componente independiente

- **Decisión**: Componente `CartDrawer` en `features/cart/components/`, no en widgets
- **Por qué**: Es una feature del carrito, no del layout. Se renderiza condicionalmente desde el Header.
- **Alternativa**: Ponerlo en widgets/ — descartado porque semanticamente pertenece al carrito.

### 2. Drawer con overlay + transición CSS

- **Decisión**: Drawer fijo a la derecha con `translate-x` y `transition-transform`, overlay oscuro
- **Por qué**: Rendimiento nativo con GPU加速, no necesita librerías externas. Tailwind tiene utilidades para translate y transition.
- **Alternativa**: Librería de drawer (headless UI) — dependencia extra innecesaria para un drawer simple.

### 3. Botón carrito en Header existente

- **Decisión**: Agregar botón con ícono SVG y badge al Header, entre nav y user info
- **Por qué**: Sin cambios al layout, solo un botón más en la fila de acciones.
- **Alternativa**: Botón flotante (FAB) — no es necesario, el header es más visible y consistente.

### 4. CartItemRow recibe callbacks, no store directo

- **Decisión**: `CartItemRow` recibe `item`, `onUpdateQuantity`, `onRemove` como props
- **Por qué**: El componente es puramente presentacional, no accede a stores. FSD: features acceden a stores, shared/components no.

### 5. Integración del botón "Agregar" en ProductDetail via prop

- **Decisión**: `ProductDetail` recibe `onAddToCart?: (product: Product) => void` y muestra el botón funcional si está presente
- **Por qué**: No queremos acoplar ProductDetail al cartStore directamente. La página orquesta: pasa el callback que llama al store.

## Risks / Trade-offs

| Riesgo                                                                   | Mitigación                                                                             |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| Drawer abierto compite con otros modales                                 | Manejar estado de apertura con un único flag. Cerrar drawer al navegar.                |
| Estado del carrito cambia mientras el drawer está abierto (ej: otro tab) | No es crítico para v1. En el futuro se puede escuchar evento `storage` para refrescar. |
| Botón "Ir a pagar" sin página de checkout creada                         | Redirigir a una página placeholder "Próximamente" con toast informativo.               |
