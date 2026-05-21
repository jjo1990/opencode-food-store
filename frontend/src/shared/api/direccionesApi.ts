import client from './client';

export interface DireccionResponse {
  id: string;
  usuario_id: string;
  alias: string | null;
  calle: string;
  numero: string;
  piso: string | null;
  departamento: string | null;
  ciudad: string;
  codigo_postal: string;
  referencia: string | null;
  es_principal: boolean;
  created_at: string;
  updated_at: string;
}

export interface DireccionCreate {
  alias?: string | null;
  calle: string;
  numero: string;
  piso?: string | null;
  departamento?: string | null;
  ciudad: string;
  codigo_postal: string;
  referencia?: string | null;
  es_principal?: boolean;
}

export interface DireccionUpdate {
  alias?: string | null;
  calle?: string;
  numero?: string;
  piso?: string | null;
  departamento?: string | null;
  ciudad?: string;
  codigo_postal?: string;
  referencia?: string | null;
  es_principal?: boolean;
}

export async function getAddresses(): Promise<DireccionResponse[]> {
  const { data } = await client.get('/direcciones');
  return data;
}

export async function getAddress(id: string): Promise<DireccionResponse> {
  const { data } = await client.get(`/direcciones/${id}`);
  return data;
}

export async function createAddress(payload: DireccionCreate): Promise<DireccionResponse> {
  const { data } = await client.post('/direcciones', payload);
  return data;
}

export async function updateAddress(
  id: string,
  payload: DireccionUpdate
): Promise<DireccionResponse> {
  const { data } = await client.put(`/direcciones/${id}`, payload);
  return data;
}

export async function setPrincipalAddress(id: string): Promise<DireccionResponse> {
  const { data } = await client.patch(`/direcciones/${id}/principal`);
  return data;
}

export async function deleteAddress(id: string): Promise<void> {
  await client.delete(`/direcciones/${id}`);
}
