import client from './client';

export interface UserProfileResponse {
  id: string;
  email: string;
  full_name: string | null;
  telefono: string | null;
  roles: string[];
  created_at: string;
}

export interface ProfileUpdateRequest {
  full_name?: string | null;
  telefono?: string | null;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

export async function getProfile(): Promise<UserProfileResponse> {
  const { data } = await client.get('/usuarios/me');
  return data;
}

export async function updateProfile(payload: ProfileUpdateRequest): Promise<UserProfileResponse> {
  const { data } = await client.put('/usuarios/me', payload);
  return data;
}

export async function changePassword(payload: PasswordChangeRequest): Promise<{ mensaje: string }> {
  const { data } = await client.put('/usuarios/me/contrasena', payload);
  return data;
}
