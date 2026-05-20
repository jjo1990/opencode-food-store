export interface ProductImage {
  url: string;
  orden: number;
}

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
  slug: string;
  descripcion: string;
  precio: number;
  stock_cantidad: number;
  disponible: boolean;
  imagenes: ProductImage[];
  categorias: ProductCategory[];
  ingredientes: ProductIngredient[];
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ProductFilters {
  search?: string;
  categoria_id?: string;
  precio_min?: number;
  precio_max?: number;
  page?: number;
  page_size?: number;
}
