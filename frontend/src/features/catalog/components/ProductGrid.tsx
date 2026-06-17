import { ProductCard } from './ProductCard';
import { Skeleton } from '../../../shared/components/Skeleton';
import { ErrorDisplay } from '../../../shared/components/ErrorDisplay';
import { EmptyState } from '../../../shared/components/EmptyState';
import type { Product } from '../../../entities/product/types';

interface ProductGridProps {
  products: Product[] | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  hasFilters: boolean;
  onRetry: () => void;
  onClearFilters: () => void;
}

export function ProductGrid({
  products,
  isLoading,
  isError,
  error,
  hasFilters,
  onRetry,
  onClearFilters,
}: ProductGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {Array.from({ length: 12 }).map((_, i) => (
          <div key={i} className="overflow-hidden rounded-xl bg-white shadow-md dark:bg-gray-800 dark:shadow-gray-900/30">
            <Skeleton variant="card" />
            <div className="space-y-2 p-4">
              <Skeleton variant="text" width="75%" />
              <Skeleton variant="text" width="40%" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorDisplay message={error?.message || 'Error al cargar los productos'} onRetry={onRetry} />
    );
  }

  if (!products || products.length === 0) {
    return (
      <EmptyState
        title="No se encontraron productos"
        description={
          hasFilters
            ? 'No hay productos que coincidan con los filtros seleccionados.'
            : 'No hay productos disponibles en este momento.'
        }
        action={hasFilters ? { label: 'Limpiar filtros', onClick: onClearFilters } : undefined}
      />
    );
  }

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}

export default ProductGrid;
