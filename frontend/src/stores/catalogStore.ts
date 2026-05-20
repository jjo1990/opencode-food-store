import { create } from 'zustand';

interface CatalogFilters {
  search: string;
  categoriaId: string | null;
  precioMin: string;
  precioMax: string;
}

interface CatalogState {
  filters: CatalogFilters;
  page: number;
  pageSize: number;

  setFilter: <K extends keyof CatalogFilters>(key: K, value: CatalogFilters[K]) => void;
  setPage: (page: number) => void;
  nextPage: () => void;
  prevPage: () => void;
  clearFilters: () => void;
}

const initialFilters: CatalogFilters = {
  search: '',
  categoriaId: null,
  precioMin: '',
  precioMax: '',
};

export const useCatalogStore = create<CatalogState>()((set) => ({
  filters: { ...initialFilters },
  page: 1,
  pageSize: 12,

  setFilter: (key, value) => {
    set((state) => ({
      filters: { ...state.filters, [key]: value },
      page: 1,
    }));
  },

  setPage: (page) => set({ page }),

  nextPage: () => set((state) => ({ page: state.page + 1 })),

  prevPage: () => set((state) => ({ page: Math.max(1, state.page - 1) })),

  clearFilters: () => {
    set({ filters: { ...initialFilters }, page: 1 });
  },
}));

export function serializeFilters(filters: CatalogFilters, page: number, pageSize: number) {
  const params = new URLSearchParams();
  if (filters.search) params.set('search', filters.search);
  if (filters.categoriaId) params.set('categoria_id', filters.categoriaId);
  if (filters.precioMin) params.set('precio_min', filters.precioMin);
  if (filters.precioMax) params.set('precio_max', filters.precioMax);
  if (page > 1) params.set('page', String(page));
  if (pageSize !== 12) params.set('page_size', String(pageSize));
  return params.toString();
}

export function parseFiltersFromURL(searchParams: URLSearchParams): {
  filters: CatalogFilters;
  page: number;
  pageSize: number;
} {
  return {
    filters: {
      search: searchParams.get('search') || '',
      categoriaId: searchParams.get('categoria_id') || null,
      precioMin: searchParams.get('precio_min') || '',
      precioMax: searchParams.get('precio_max') || '',
    },
    page: parseInt(searchParams.get('page') || '1', 10),
    pageSize: parseInt(searchParams.get('page_size') || '12', 10),
  };
}
