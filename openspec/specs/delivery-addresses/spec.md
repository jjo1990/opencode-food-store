# delivery-addresses Specification

## Purpose

TBD - created by archiving change implement-delivery-addresses-crud. Update Purpose after archive.

## Requirements

### Requirement: User can create a delivery address

The system SHALL allow an authenticated user (rol CLIENT) to create a new delivery address.

The address SHALL include: alias (optional), calle, numero, piso (optional), departamento (optional), ciudad, codigo_postal, referencia (optional), es_principal (boolean, default false).

If the user has NO existing active addresses, the new address SHALL be automatically marked as `es_principal = true` regardless of the request value.

#### Scenario: Create first address

- **WHEN** an authenticated user creates their first address
- **THEN** the address is created and automatically set as `es_principal = true`
- **AND** the response includes all address fields with `id` and `es_principal = true`

#### Scenario: Create additional address

- **WHEN** an authenticated user with existing addresses creates a new address with `es_principal = false`
- **THEN** the address is created with `es_principal = false`
- **AND** the existing principal address remains unchanged

#### Scenario: Create address and set as new principal

- **WHEN** an authenticated user with existing addresses creates a new address with `es_principal = true`
- **THEN** the address is created with `es_principal = true`
- **AND** the previous principal address is set to `es_principal = false`

#### Scenario: Create address without authentication

- **WHEN** an unauthenticated request tries to create an address
- **THEN** the system returns HTTP 401 Unauthorized

#### Scenario: Create address with invalid data

- **WHEN** a request misses required fields (calle, numero, ciudad, codigo_postal)
- **THEN** the system returns HTTP 422 Unprocessable Entity with validation errors

### Requirement: User can list their delivery addresses

The system SHALL return all active (not soft-deleted) addresses belonging to the authenticated user.

The list SHALL return the principal address first, ordered by `created_at DESC`.

#### Scenario: List addresses with data

- **WHEN** an authenticated user requests their addresses
- **THEN** the system returns HTTP 200 with an array of addresses
- **AND** the principal address is first in the array

#### Scenario: List addresses when empty

- **WHEN** an authenticated user with no addresses requests the list
- **THEN** the system returns HTTP 200 with an empty array

#### Scenario: List addresses excludes other users' addresses

- **WHEN** an authenticated user requests their addresses
- **THEN** the response SHALL NOT include addresses belonging to other users

### Requirement: User can view a single delivery address

The system SHALL return a specific address by ID if it belongs to the authenticated user and is not soft-deleted.

#### Scenario: View own address

- **WHEN** an authenticated user requests their own address by ID
- **THEN** the system returns HTTP 200 with the full address details

#### Scenario: View another user's address

- **WHEN** an authenticated user requests an address belonging to another user
- **THEN** the system returns HTTP 404 Not Found (no revelar existencia)

#### Scenario: View soft-deleted address

- **WHEN** an authenticated user requests their own address that was soft-deleted
- **THEN** the system returns HTTP 404 Not Found

### Requirement: User can update a delivery address

The system SHALL allow an authenticated user to update their own address fields.

Updates SHALL be partial — only provided fields are changed.

If the user sets `es_principal = true`, the previous principal address SHALL be set to `es_principal = false`.

#### Scenario: Update address fields

- **WHEN** an authenticated user updates their address with new calle and ciudad
- **THEN** the system returns HTTP 200 with the updated address
- **AND** only the specified fields are changed

#### Scenario: Update to set as principal

- **WHEN** an authenticated user updates an existing address setting `es_principal = true`
- **THEN** the address becomes the new principal
- **AND** the previous principal address is set to `es_principal = false`

#### Scenario: Update another user's address

- **WHEN** an authenticated user tries to update an address belonging to another user
- **THEN** the system returns HTTP 404 Not Found

#### Scenario: Update with empty body

- **WHEN** an authenticated user sends an update with no fields to change
- **THEN** the system returns HTTP 400 Bad Request with "No hay datos para actualizar"

### Requirement: User can delete a delivery address

The system SHALL allow an authenticated user to soft-delete their own address.

If the address is the user's ONLY active address, the system SHALL reject the deletion.

If the deleted address was the principal address, the system SHALL NOT auto-assign a new principal.

#### Scenario: Delete secondary address

- **WHEN** an authenticated user deletes a secondary (non-principal) address
- **THEN** the system returns HTTP 204 No Content
- **AND** the address is soft-deleted (soft_deleted_at is set)

#### Scenario: Delete only address

- **WHEN** an authenticated user tries to delete their only active address
- **THEN** the system returns HTTP 400 Bad Request
- **AND** the error explains: "No puedes eliminar tu única dirección de entrega"

#### Scenario: Delete principal address when others exist

- **WHEN** an authenticated user with multiple addresses deletes their principal address
- **THEN** the system returns HTTP 204 No Content
- **AND** the address is soft-deleted
- **AND** no other address is auto-promoted to principal

#### Scenario: Delete another user's address

- **WHEN** an authenticated user tries to delete an address belonging to another user
- **THEN** the system returns HTTP 404 Not Found

### Requirement: User can set an address as principal

The system SHALL expose a dedicated endpoint to set any of the user's active addresses as the principal address.

If the address is already principal, the system SHALL return success with no changes.

The previous principal SHALL be set to `es_principal = false`.

#### Scenario: Set address as principal

- **WHEN** an authenticated user calls the set-principal endpoint on their secondary address
- **THEN** the system returns HTTP 200 with the updated address
- **AND** that address's `es_principal` becomes `true`
- **AND** the previous principal's `es_principal` becomes `false`

#### Scenario: Set already-principal address as principal

- **WHEN** an authenticated user calls the set-principal endpoint on their current principal address
- **THEN** the system returns HTTP 200 with no changes

#### Scenario: Set another user's address as principal

- **WHEN** an authenticated user tries to set another user's address as principal
- **THEN** the system returns HTTP 404 Not Found

### Requirement: Delivery addresses are protected by authentication

All delivery address endpoints SHALL require authentication.

Addresses SHALL be scoped to the authenticated user — no user can access another user's addresses.

List and detail endpoints SHALL use `get_current_user` (any authenticated user).
Create, update, delete, and set-principal endpoints SHALL use `require_role("CLIENT")`.

#### Scenario: All endpoints require auth

- **WHEN** an unauthenticated request hits any `/api/v1/direcciones/*` endpoint
- **THEN** the system returns HTTP 401 Unauthorized
