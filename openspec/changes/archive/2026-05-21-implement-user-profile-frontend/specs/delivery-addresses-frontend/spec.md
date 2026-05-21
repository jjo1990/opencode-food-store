## ADDED Requirements

### Requirement: User can view their delivery addresses

The system SHALL display all active delivery addresses for the authenticated user.

The page SHALL show a loading skeleton while addresses are being fetched.
If the fetch fails, the system SHALL display an error message with a retry button.
If the user has no addresses, the system SHALL show an EmptyState with "Aún no tienes direcciones guardadas" and a button "Agregar dirección".
The principal address SHALL be visually distinguished (e.g., badge "Principal").
Addresses SHALL be ordered with the principal first, then by creation date.

#### Scenario: View addresses successfully

- **WHEN** the authenticated user navigates to `/addresses`
- **THEN** the page shows a skeleton while loading
- **THEN** the addresses are displayed as cards with principal badge on the first one

#### Scenario: No addresses

- **WHEN** the authenticated user has no addresses
- **THEN** an EmptyState is shown with "Aún no tienes direcciones guardadas" and a CTA button

#### Scenario: Fetch fails

- **WHEN** the addresses fetch returns an error
- **THEN** an ErrorDisplay is shown with retry button

### Requirement: User can create a new address

The system SHALL provide a form (modal) to create a new delivery address.

The form SHALL include: alias (optional), calle (required), numero (required), piso (optional), departamento (optional), ciudad (required), codigo_postal (required), referencia (optional), es_principal (checkbox, optional).

Validation: required fields must not be empty, codigo_postal max 20 chars.
On success: close modal, show success toast ("Dirección creada correctamente"), refresh addresses list.
On failure: show error inline in modal, keep modal open.

#### Scenario: Open create address modal

- **WHEN** the user clicks "Agregar dirección"
- **THEN** a modal opens with an empty address form

#### Scenario: Create address successfully

- **WHEN** the user fills all required fields and clicks "Guardar"
- **THEN** the system calls `POST /api/v1/direcciones`
- **AND** the modal closes
- **AND** a success toast is shown
- **AND** the addresses list refreshes

#### Scenario: Create address with missing required fields

- **WHEN** the user clicks "Guardar" without filling calle, numero, ciudad, or codigo_postal
- **THEN** the system shows inline validation errors on the empty fields
- **AND** the modal stays open

### Requirement: User can edit an address

The system SHALL provide a form (modal) pre-filled with the address data for editing.

The form SHALL be the same as the create form, but pre-populated with existing values.
On success: close modal, show toast, refresh list.
On failure: show error inline, keep modal open.

#### Scenario: Edit address successfully

- **WHEN** the user clicks "Editar" on an address card
- **THEN** a modal opens with the address data pre-filled
- **WHEN** the user modifies fields and clicks "Guardar"
- **THEN** the system calls `PUT /api/v1/direcciones/{id}`
- **AND** the modal closes with success toast
- **AND** the addresses list refreshes

### Requirement: User can delete an address

The system SHALL allow the user to delete an address with a confirmation dialog.

Before deletion, a confirmation modal SHALL display: "¿Estás seguro de eliminar esta dirección?" with the address summary and "Eliminar" / "Cancelar" buttons.
On success: close modal, show toast ("Dirección eliminada"), refresh list.
On failure: show error toast.

#### Scenario: Delete address with confirmation

- **WHEN** the user clicks "Eliminar" on an address card
- **THEN** a confirmation modal appears with the address summary
- **WHEN** the user clicks "Eliminar" in the confirmation
- **THEN** the system calls `DELETE /api/v1/direcciones/{id}`
- **AND** shows a success toast
- **AND** refreshes the list

#### Scenario: Cancel deletion

- **WHEN** the confirmation modal is open and the user clicks "Cancelar"
- **THEN** the modal closes
- **AND** the address is not deleted

### Requirement: User can set an address as principal

The system SHALL allow the user to mark any address as the principal delivery address.

A "Set as principal" button/action SHALL be available on non-principal addresses.
On success: show toast ("Dirección principal actualizada"), refresh list.
If the address is already principal, the action SHALL be hidden or disabled.

#### Scenario: Set address as principal

- **WHEN** the user clicks "Establecer como principal" on a non-principal address
- **THEN** the system calls `PATCH /api/v1/direcciones/{id}/principal`
- **AND** shows a success toast
- **AND** the addresses list refreshes with the new principal marked

### Requirement: Addresses page has proper navigation

The system SHALL include "Mis Direcciones" in the user's navigation.
The `/addresses` route SHALL be registered in the router with ProtectedRoute requiring CLIENT role.

#### Scenario: Addresses route is protected

- **WHEN** an unauthenticated user navigates to `/addresses`
- **THEN** they are redirected to `/login`
