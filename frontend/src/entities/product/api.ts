import { useQuery } from '@tanstack/react-query';
import { fetchProducts, fetchProductById } from '../../shared/api/catalogApi';
import type { ProductFilters, Product, ProductListResponse } from './types';

export function useProducts(filters: ProductFilters) {
  return useQuery<ProductListResponse>({
    queryKey: ['products', filters],
    queryFn: () => fetchProducts(filters),
    placeholderData: (prev) => prev,
  });
}

export function useProduct(id: string) {
  return useQuery<Product>({
    queryKey: ['product', id],
    queryFn: () => fetchProductById(id),
    enabled: !!id,
  });
}
