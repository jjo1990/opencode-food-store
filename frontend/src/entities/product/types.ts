export interface ProductCategory {
  id: string;
  nombre: string;
  slug: string;
}

export interface ProductIngredient {
  id: string;
  nombre: string;
  es_alergeno: boolean;
}

export interface Product {
  id: string;
  nombre: string;
  descripcion: string;
  precio_base: number;
  stock_cantidad: number;
  disponible: boolean;
  imagen_url: string | null;
  categorias: ProductCategory[];
  ingredientes: ProductIngredient[];
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  skip: number;
  limit: number;
}

export interface ProductFilters {
  search?: string;
  categoria_id?: string;
  precio_min?: number;
  precio_max?: number;
  page?: number;
  page_size?: number;
}
