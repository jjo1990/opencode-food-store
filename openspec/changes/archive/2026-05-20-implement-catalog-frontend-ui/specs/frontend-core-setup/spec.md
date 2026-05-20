# Spec: frontend-core-setup

## Overview

Configuración base del frontend necesaria para que cualquier feature funcione: Router con React Router, Providers (TanStack Query, Toaster), cliente Axios compartido, y Tailwind CSS con design tokens.

## ADDED Requirements

### Requirement: Router con layout compartido

El sistema SHALL tener un router configurado con React Router v6 con layout compartido (Header/Nav/Footer) y rutas definidas.

#### Scenario: Router monta layout compartido

- **WHEN** el usuario navega a cualquier ruta
- **THEN** se renderiza el layout compartido con Header (logo, nav links, auth status) y Footer
- **AND** el contenido de la ruta se renderiza en un `<Outlet />`

#### Scenario: Ruta catálogo funciona

- **WHEN** el usuario navega a `/catalog`
- **THEN** se renderiza CatalogPage con la grilla de productos
- **AND** `/catalog` es accesible sin autenticación

#### Scenario: Ruta detalle funciona

- **WHEN** el usuario navega a `/catalog/:slug`
- **THEN** se renderiza ProductDetailPage con la información del producto
- **AND** `/catalog/:slug` es accesible sin autenticación

#### Scenario: Ruta no encontrada

- **WHEN** el usuario navega a una ruta que no existe
- **THEN** se muestra una página 404 con mensaje y botón para volver al inicio

### Requirement: TanStack Query Provider configurado

El sistema SHALL tener un `QueryClientProvider` configurado con defaults sensatos para toda la app.

#### Scenario: Provider montado en el root

- **WHEN** la aplicación se inicializa
- **THEN** el árbol de componentes tiene un `QueryClientProvider` en el root
- **AND** el QueryClient tiene `staleTime: 30000` (30s) y `retry: 1`

#### Scenario: Devtools en desarrollo

- **WHEN** la aplicación corre en modo desarrollo (`VITE_DEV === 'true'` o similar)
- **THEN** `ReactQueryDevtools` están disponibles como floating panel

### Requirement: Axios client compartido

El sistema SHALL tener un Axios instance compartido con baseURL configurada e interceptores de JWT y error handling.

#### Scenario: Client usa VITE_API_BASE_URL

- **WHEN** se importa el client desde `shared/api/client`
- **THEN** el Axios instance tiene `baseURL` igual a `VITE_API_BASE_URL || 'http://localhost:8000/api/v1'`

#### Scenario: Interceptor attach JWT

- **WHEN** se hace una petición con el client
- **THEN** si existe un accessToken en authStore, se agrega como `Authorization: Bearer <token>`

#### Scenario: Error handling consistente

- **WHEN** una petición HTTP falla
- **THEN** se muestra un toast con el mensaje de error (usando react-hot-toast)
- **AND** los errores 401 limpian el token del authStore

### Requirement: Tailwind CSS configurado con design tokens

El sistema SHALL tener Tailwind CSS v3 configurado con PostCSS y design tokens personalizados para el proyecto.

#### Scenario: Tailwind procesa clases utilitarias

- **WHEN** se renderiza un elemento con clases Tailwind (ej: `className="text-primary-500 bg-gray-100 p-4 rounded-lg"`)
- **THEN** los estilos se aplican correctamente con los tokens del proyecto

#### Scenario: Design tokens disponibles

- **WHEN** se usa `text-primary` o `bg-primary`
- **THEN** aplica el color primary definido en tailwind.config (verde/azul institucional)
- **WHEN** se usa `text-secondary`
- **THEN** aplica el color secondary
- **WHEN** se usa `rounded-lg` o `shadow-md`
- **THEN** aplica los valores del design system

### Requirement: Toaster global configurado

El sistema SHALL tener un Toaster de `react-hot-toast` global en el root de la aplicación.

#### Scenario: Toast se muestra globalmente

- **WHEN** cualquier componente llama a `toast.success('Mensaje')` o `toast.error('Error')`
- **THEN** el toast aparece en la esquina superior derecha
- **AND** el toast se oculta automáticamente después de 4 segundos (success) o 5 segundos (error)
