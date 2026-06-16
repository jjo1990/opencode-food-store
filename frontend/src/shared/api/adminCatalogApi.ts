import client from './client';

export interface AdminProductoListItem {
  id: string;
  nombre: string;
  precio_base: number;
  stock_cantidad: number;
  disponible: boolean;
  eliminado: boolean;
  soft_deleted_at: string | null;
  created_at: string;
  categorias: string[];
}

export interface AdminProductoListResponse {
  items: AdminProductoListItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface AdminCategoriaListItem {
  id: string;
  nombre: string;
  parent_id: string | null;
  eliminado: boolean;
  soft_deleted_at: string | null;
  created_at: string;
}

export interface AdminCategoriaListResponse {
  items: AdminCategoriaListItem[];
  total: number;
}

export interface AdminIngredienteListItem {
  id: string;
  nombre: string;
  es_alergeno: boolean;
  eliminado: boolean;
  soft_deleted_at: string | null;
  created_at: string;
}

export interface AdminIngredienteListResponse {
  items: AdminIngredienteListItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface AdminProductosParams {
  page?: number;
  size?: number;
  search?: string;
  disponible?: boolean;
  eliminado?: boolean;
  categoria_id?: string;
}

export interface AdminIngredientesParams {
  page?: number;
  size?: number;
  es_alergeno?: boolean;
  eliminado?: boolean;
}

export async function fetchAdminProductos(
  params: AdminProductosParams = {}
): Promise<AdminProductoListResponse> {
  const queryParams: Record<string, string | number | boolean> = {};
  if (params.page) queryParams.page = params.page;
  if (params.size) queryParams.size = params.size;
  if (params.search) queryParams.search = params.search;
  if (params.disponible !== undefined) queryParams.disponible = params.disponible;
  if (params.eliminado !== undefined) queryParams.eliminado = params.eliminado;
  if (params.categoria_id) queryParams.categoria_id = params.categoria_id;

  const response = await client.get<AdminProductoListResponse>('/admin/productos', {
    params: queryParams,
  });
  return response.data;
}

export async function fetchAdminCategorias(
  eliminado?: boolean
): Promise<AdminCategoriaListResponse> {
  const params: Record<string, boolean> = {};
  if (eliminado !== undefined) params.eliminado = eliminado;

  const response = await client.get<AdminCategoriaListResponse>('/admin/categorias', { params });
  return response.data;
}

export async function fetchAdminIngredientes(
  params: AdminIngredientesParams = {}
): Promise<AdminIngredienteListResponse> {
  const queryParams: Record<string, string | number | boolean> = {};
  if (params.page) queryParams.page = params.page;
  if (params.size) queryParams.size = params.size;
  if (params.es_alergeno !== undefined) queryParams.es_alergeno = params.es_alergeno;
  if (params.eliminado !== undefined) queryParams.eliminado = params.eliminado;

  const response = await client.get<AdminIngredienteListResponse>('/admin/ingredientes', {
    params: queryParams,
  });
  return response.data;
}
