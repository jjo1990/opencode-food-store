import { useQuery } from '@tanstack/react-query';
import { fetchCategories } from '../../shared/api/catalogApi';
import type { Category } from './types';

export function useCategories() {
  return useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: fetchCategories,
    staleTime: 5 * 60 * 1000,
  });
}
