# Spec: shared-ui

## Overview

Componentes base reutilizables del design system del frontend (Button, Card, Input, Spinner, Skeleton, Pagination, ErrorDisplay, EmptyState). Sirven como building blocks para todas las features del proyecto.

## ADDED Requirements

### Requirement: Button soporta variantes visuales

El sistema SHALL proveer un componente `Button` reutilizable con variantes visuales y estados.

#### Scenario: Renderizado por variante

- **WHEN** se renderiza un Button sin props adicionales
- **THEN** se muestra como botón primary (fondo primary, texto blanco)
- **WHEN** se pasa `variant="secondary"`
- **THEN** se muestra como botón secondary (borde primary, texto primary)
- **WHEN** se pasa `variant="ghost"`
- **THEN** se muestra como botón ghost (sin fondo ni borde)
- **WHEN** se pasa `variant="danger"`
- **THEN** se muestra como botón danger (fondo rojo, texto blanco)

#### Scenario: Estados del botón

- **WHEN** se pasa `disabled={true}`
- **THEN** el botón se renderiza con opacidad reducida y cursor no permitido
- **AND** no dispara onClick
- **WHEN** se pasa `isLoading={true}`
- **THEN** el botón muestra un spinner pequeño y deshabilita la interacción
- **WHEN** se pasa `as="a"` con `href`
- **THEN** se renderiza como un tag `<a>` con los mismos estilos

### Requirement: Card es contenedor visual consistente

El sistema SHALL proveer un componente `Card` que encapsule contenido con sombra, bordes redondeados y padding consistente.

#### Scenario: Card por defecto

- **WHEN** se renderiza un Card con children
- **THEN** se muestra un contenedor con sombra suave, border-radius y padding

#### Scenario: Card con hover effect

- **WHEN** se pasa `hoverable={true}`
- **THEN** el card tiene efecto de elevación al hacer hover (sombra más pronunciada)

### Requirement: Input con label y error state

El sistema SHALL proveer un componente `Input` con label, placeholder y estado de error integrados.

#### Scenario: Input por defecto

- **WHEN** se renderiza un Input con `label` y `placeholder`
- **THEN** se muestra el label arriba del input y el placeholder dentro

#### Scenario: Input en estado de error

- **WHEN** se pasa `error="Mensaje de error"`
- **THEN** el borde del input se vuelve rojo
- **AND** se muestra el mensaje de error debajo del input en texto rojo

### Requirement: Spinner de carga animado

El sistema SHALL proveer un componente `Spinner` para indicar operaciones en progreso.

#### Scenario: Spinner por defecto

- **WHEN** se renderiza un Spinner sin props
- **THEN** se muestra un círculo animado rotando (color primary)

#### Scenario: Spinner con tamaño variable

- **WHEN** se pasa `size="sm"`, `size="md"` o `size="lg"`
- **THEN** el spinner se renderiza en 16px, 24px o 40px respectivamente

### Requirement: Skeleton para estados de carga

El sistema SHALL proveer un componente `Skeleton` para mostrar placeholders animados mientras se cargan datos.

#### Scenario: Skeleton por defecto

- **WHEN** se renderiza un Skeleton
- **THEN** se muestra un rectángulo gris con animación de pulse/shine

#### Scenario: Skeleton con variantes

- **WHEN** se pasa `variant="text"`
- **THEN** se muestra como una línea de texto (ancho configurable)
- **WHEN** se pasa `variant="circle"`
- **THEN** se muestra como un círculo (útil para avatares)
- **WHEN** se pasa `variant="card"`
- **THEN** se muestra con la estructura de una card (rectángulo con espacio para imagen + texto)

### Requirement: Pagination para navegación entre páginas

El sistema SHALL proveer un componente `Pagination` para navegar entre páginas de resultados.

#### Scenario: Paginación por defecto

- **WHEN** se renderiza Pagination con `currentPage`, `totalPages` y `onPageChange`
- **THEN** se muestran botones: Anterior, números de página, Siguiente
- **AND** la página actual se muestra con estilo activo

#### Scenario: Paginación con muchas páginas

- **WHEN** `totalPages > 7`
- **THEN** se muestran números de página con ellipsis (ej: 1 ... 4 5 6 ... 10)

#### Scenario: Botones deshabilitados

- **WHEN** `currentPage === 1`
- **THEN** el botón "Anterior" está deshabilitado
- **WHEN** `currentPage === totalPages`
- **THEN** el botón "Siguiente" está deshabilitado

### Requirement: ErrorDisplay para estados de error

El sistema SHALL proveer un componente `ErrorDisplay` para mostrar errores de manera consistente.

#### Scenario: Error con reintento

- **WHEN** se renderiza ErrorDisplay con `message` y `onRetry`
- **THEN** se muestra el mensaje de error con un icono de advertencia
- **AND** se muestra un botón "Reintentar" que ejecuta `onRetry`

#### Scenario: Error sin reintento

- **WHEN** se renderiza ErrorDisplay con solo `message`
- **THEN** se muestra el mensaje de error sin botón de reintento

### Requirement: EmptyState para listas vacías

El sistema SHALL proveer un componente `EmptyState` para mostrar cuando no hay datos.

#### Scenario: EmptyState por defecto

- **WHEN** se renderiza EmptyState con `title` y `description`
- **THEN** se muestra el título, descripción y un icono de "vacío"
- **WHEN** se pasa `action={{ label: "Acción", onClick }}`
- **THEN** se muestra un botón con el label que ejecuta onClick
