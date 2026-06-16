import client from './client';

export interface SystemConfigAuditItem {
  updated_by: string | null;
  updated_by_name: string | null;
  updated_at: string | null;
}

export interface SystemConfigResponse {
  configuracion: Record<string, string>;
  auditoria: Record<string, SystemConfigAuditItem>;
}

export interface SystemConfigUpdateRequest {
  configuracion: Record<string, string>;
}

export async function fetchConfig(): Promise<SystemConfigResponse> {
  const response = await client.get<SystemConfigResponse>('/admin/configuracion');
  return response.data;
}

export async function updateConfig(body: SystemConfigUpdateRequest): Promise<SystemConfigResponse> {
  const response = await client.put<SystemConfigResponse>('/admin/configuracion', body);
  return response.data;
}
