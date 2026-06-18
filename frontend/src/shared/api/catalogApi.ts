import client from './client';

export interface ProductoResponse {
  id: string;
  nombre: string;
  descripcion: string;
  precio_base: number;
  stock_cantidad: number;
  disponible: boolean;
  imagen_url: string | null;
  categorias: { id: string; nombre: string; slug: string }[];
  ingredientes: { id: string; nombre: string; es_alergeno: boolean }[];
}

export interface ProductoListResponse {
  items: ProductoResponse[];
  total: number;
  skip: number;
  limit: number;
}

export interface CategoriaResponse {
  id: string;
  nombre: string;
  slug: string;
  children: CategoriaResponse[];
}

export interface ProductFilters {
  search?: string;
  categoria_id?: string;
  precio_min?: number;
  precio_max?: number;
  page?: number;
  page_size?: number;
}

export async function fetchProducts(filters: ProductFilters = {}): Promise<ProductoListResponse> {
  const params: Record<string, string | number> = {};
  if (filters.search) params.search = filters.search;
  if (filters.categoria_id) params.categoria_id = filters.categoria_id;
  if (filters.precio_min !== undefined) params.precio_min = filters.precio_min;
  if (filters.precio_max !== undefined) params.precio_max = filters.precio_max;
  if (filters.page) params.page = filters.page;
  if (filters.page_size) params.page_size = filters.page_size;

  const response = await client.get<ProductoListResponse>('/productos', { params });
  return response.data;
}

export async function fetchProductById(id: string): Promise<ProductoResponse> {
  const response = await client.get<ProductoResponse>(`/productos/${id}`);
  return response.data;
}

export async function fetchCategories(): Promise<CategoriaResponse[]> {
  const response = await client.get<CategoriaResponse[]>('/categorias');
  return response.data;
}
