## ADDED Requirements

### Requirement: User can view their profile

The system SHALL display the authenticated user's profile information (nombre, email, teléfono) in a read-only form that switches to editable on demand.

The page SHALL show a loading skeleton while the profile is being fetched.
If the profile fetch fails, the system SHALL display an error message with a retry button.
The page SHALL use `useProfile` hook from `entities/user/api.ts`.

#### Scenario: View profile successfully

- **WHEN** the authenticated user navigates to `/profile`
- **THEN** the page shows a skeleton while loading
- **THEN** the profile displays nombre, email, and teléfono in read-only mode

#### Scenario: Profile fetch fails

- **WHEN** the profile fetch returns an error
- **THEN** the system displays an ErrorDisplay component with the error message and a retry button

### Requirement: User can update their name and phone

The system SHALL allow the authenticated user to edit their `full_name` and `telefono` fields inline.

The form SHALL validate: full_name (min 2 chars), telefono (optional, max 20 chars).
On successful save, the system SHALL show a success toast ("Perfil actualizado correctamente").
On save failure, the system SHALL show an error toast with the server error message.

#### Scenario: Update profile successfully

- **WHEN** the user clicks "Editar" on their profile
- **THEN** the fields become editable inputs
- **WHEN** the user modifies nombre and telefono and clicks "Guardar"
- **THEN** the system calls `PUT /api/v1/usuarios/me`
- **AND** shows a success toast
- **AND** the fields return to read-only mode with updated values

#### Scenario: Cancel profile edit

- **WHEN** the user clicks "Editar" and then clicks "Cancelar"
- **THEN** the fields revert to their original values
- **AND** return to read-only mode

#### Scenario: Update with invalid data

- **WHEN** the user enters a full_name shorter than 2 characters
- **THEN** the system shows inline validation error "El nombre debe tener al menos 2 caracteres"
- **AND** the save button is disabled

### Requirement: User can change their password

The system SHALL allow the authenticated user to change their password via a modal dialog.

The modal SHALL contain: current password input, new password input, confirm new password input.
Validation: all fields required, new password ≥ 8 chars, new password matches confirm.
On success: close modal, show success toast ("Contraseña actualizada correctamente").
On failure: show error inline in modal, keep modal open.

#### Scenario: Open password change modal

- **WHEN** the user clicks "Cambiar contraseña" on the profile page
- **THEN** a modal opens with three password fields

#### Scenario: Change password successfully

- **WHEN** the user enters current password, new password (≥8 chars), and confirmation match
- **WHEN** the user clicks "Guardar"
- **THEN** the system calls `PUT /api/v1/usuarios/me/contrasena`
- **AND** the modal closes
- **AND** a success toast is shown

#### Scenario: Password mismatch

- **WHEN** the new password and confirm password do not match
- **THEN** the system shows inline error "Las contraseñas no coinciden"
- **AND** the save button is disabled

#### Scenario: Change password fails

- **WHEN** the API returns an error (e.g. wrong current password)
- **THEN** the modal stays open
- **AND** an error message is shown inside the modal: "Contraseña actual incorrecta"

### Requirement: Profile page has proper navigation

The system SHALL include "Mi Perfil" in the user's navigation (visible when authenticated).
The `/profile` route SHALL be registered in the router with ProtectedRoute requiring CLIENT role.

#### Scenario: Profile route is protected

- **WHEN** an unauthenticated user navigates to `/profile`
- **THEN** they are redirected to `/login`
