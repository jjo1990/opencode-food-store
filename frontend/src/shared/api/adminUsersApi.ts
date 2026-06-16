import client from './client';

export interface AdminUserResponse {
  id: string;
  email: string;
  full_name: string | null;
  telefono: string | null;
  roles: string[];
  activo: boolean;
  created_at: string;
  soft_deleted_at: string | null;
}

export interface AdminUserListResponse {
  items: AdminUserResponse[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface AdminUserUpdateRequest {
  full_name?: string | null;
  email?: string | null;
  telefono?: string | null;
  roles?: string[];
}

export interface AdminUsersParams {
  page?: number;
  size?: number;
  rol?: string;
  search?: string;
  estado?: string;
}

export async function fetchAdminUsers(
  params: AdminUsersParams = {}
): Promise<AdminUserListResponse> {
  const queryParams: Record<string, string | number> = {};
  if (params.page) queryParams.page = params.page;
  if (params.size) queryParams.size = params.size;
  if (params.rol) queryParams.rol = params.rol;
  if (params.search) queryParams.search = params.search;
  if (params.estado) queryParams.estado = params.estado;

  const response = await client.get<AdminUserListResponse>('/admin/usuarios', {
    params: queryParams,
  });
  return response.data;
}

export async function fetchAdminUser(id: string): Promise<AdminUserResponse> {
  const response = await client.get<AdminUserResponse>(`/admin/usuarios/${id}`);
  return response.data;
}

export async function updateAdminUser(
  id: string,
  body: AdminUserUpdateRequest
): Promise<AdminUserResponse> {
  const response = await client.put<AdminUserResponse>(`/admin/usuarios/${id}`, body);
  return response.data;
}

export async function deleteAdminUser(id: string): Promise<{ message: string }> {
  const response = await client.delete<{ message: string }>(`/admin/usuarios/${id}`);
  return response.data;
}

export async function reactivateAdminUser(id: string): Promise<AdminUserResponse> {
  const response = await client.patch<AdminUserResponse>(`/admin/usuarios/${id}/reactivar`);
  return response.data;
}
