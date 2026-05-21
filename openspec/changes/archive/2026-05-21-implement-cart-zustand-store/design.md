## Context

El frontend ya tiene 2 stores Zustand:

- `authStore` — estado de autenticación con persist + middleware, llamadas asincrónicas a API
- `catalogStore` — estado de UI (filtros, paginación), puramente sincrónico, sin persist

Ambos usan Zustand v5 con la sintaxis `create<State>()((set, get) => ({...}))`.

El carrito necesita persistencia local (sobrevivir a cierre del navegador), acciones sincrónicas (no necesita API — es estado del cliente), y selectores derivados (totalItems, totalPrice).

## Goals / Non-Goals

**Goals:**

- Store Zustand con tipo estricto para el carrito
- Persistencia en localStorage
- Acciones: agregar, actualizar cantidad, eliminar item, vaciar carrito, actualizar personalización
- Selectores: totalItems, totalPrice, getItem
- Si un producto ya existe en el carrito al agregar, incrementar cantidad en vez de duplicar

**Non-Goals:**

- Sincronización con backend (es carrito local, no persiste en servidor)
- Validación de stock (se hará en checkout validation — Change 27)
- Cálculo de envío (se hará en order creation — Change 28)
- Límite máximo de items

## Decisions

### 1. Store único con persist

- **Decisión**: Store único con `persist` middleware, misma sintaxis que `authStore`
- **Por qué**: Consistencia con stores existentes. `persist` maneja automáticamente serialización/deserialización.
- **Alternativa**: Store sin persist + localStorage manual — descartado porque `persist` maneja edge cases (SSR, migraciones de schema).

### 2. CartItem con snapshot de datos del producto

- **Decisión**: `CartItem` incluye `nombre`, `imagen_url`, `precio` (copia del producto al momento de agregar)
- **Por qué**: El precio puede cambiar en el backend. El carrito muestra el precio AL MOMENTO de agregar. En checkout validation (Change 27) se comparará con el precio actual.
- **Alternativa**: Solo almacenar producto_id y resolver nombre/precio vía API en el frontend — descartado porque el carrito debe funcionar offline y ser instantáneo.

### 3. personalizacion como string[]

- **Decisión**: `personalizacion` es un array de IDs de ingredientes a REMOVER
- **Por qué**: Coincide con el modelo del backend (ProductoIngrediente con es_removible). El backend espera `personalizacion: ingredientIds[]` al crear el pedido.
- **Alternativa**: Objeto con inclusiones/exclusiones — sobre-ingeniería para v1. Solo removemos ingredientes.

### 4. Sin acciones asincrónicas

- **Decisión**: Todas las acciones son sincrónicas. No llaman a ninguna API.
- **Por qué**: El carrito es estado 100% del cliente. Las interacciones con el backend (validación, creación de pedido) se manejan en features/pages separadas con TanStack Query.

## Risks / Trade-offs

| Riesgo                                                                         | Mitigación                                                                                                                                 |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| El precio snapshot puede quedar desactualizado si el admin cambia precios      | En checkout validation (Change 27) se comparará precio snapshot vs precio actual y se mostrará advertencia                                 |
| Persistencia en localStorage con items grandes (muchos productos con imágenes) | Solo se almacenan strings (IDs, URLs), no datos binarios. Límite de localStorage ~5MB es suficiente para cientos de items.                 |
| Dos pestañas abiertas pueden tener carritos inconsistentes                     | `persist` no sincroniza entre pestañas. Se puede agregar un listener `storage` event en el futuro si es necesario (no es crítico para v1). |
