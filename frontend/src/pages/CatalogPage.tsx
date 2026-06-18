import { useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useProducts } from '../entities/product/api';
import { useCategories } from '../entities/category/api';
import { useCatalogStore } from '../stores/catalogStore';
import { serializeFilters, parseFiltersFromURL } from '../stores/catalogStore';
import { ProductGrid } from '../features/catalog/components/ProductGrid';
import { CategoryNav } from '../features/catalog/components/CategoryNav';
import { ProductFilters } from '../features/catalog/components/ProductFilters';
import { PaginationBar } from '../features/catalog/components/PaginationBar';

export function CatalogPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters = useCatalogStore((s) => s.filters);
  const page = useCatalogStore((s) => s.page);
  const pageSize = useCatalogStore((s) => s.pageSize);
  const setFilter = useCatalogStore((s) => s.setFilter);
  const setPage = useCatalogStore((s) => s.setPage);
  const clearFilters = useCatalogStore((s) => s.clearFilters);

  useEffect(() => {
    const parsed = parseFiltersFromURL(searchParams);
    setFilter('search', parsed.filters.search);
    setFilter('categoriaId', parsed.filters.categoriaId);
    setFilter('precioMin', parsed.filters.precioMin);
    setFilter('precioMax', parsed.filters.precioMax);
    setPage(parsed.page);
  }, []);

  const syncUrl = useCallback(() => {
    const currentFilters = useCatalogStore.getState().filters;
    const currentPage = useCatalogStore.getState().page;
    const currentPageSize = useCatalogStore.getState().pageSize;
    const qs = serializeFilters(currentFilters, currentPage, currentPageSize);
    setSearchParams(qs, { replace: true });
  }, [setSearchParams]);

  const apiFilters = {
    search: filters.search || undefined,
    categoria_id: filters.categoriaId || undefined,
    precio_min: filters.precioMin ? Number(filters.precioMin) : undefined,
    precio_max: filters.precioMax ? Number(filters.precioMax) : undefined,
    page,
    page_size: pageSize,
  };

  const {
    data: productData,
    isLoading: productsLoading,
    isError: productsError,
    error: productsErrorObj,
    refetch: refetchProducts,
  } = useProducts(apiFilters);

  const {
    data: categories,
    isLoading: categoriesLoading,
    isError: categoriesError,
    error: categoriesErrorObj,
    refetch: refetchCategories,
  } = useCategories();

  const hasActiveFilters =
    !!filters.search || !!filters.categoriaId || !!filters.precioMin || !!filters.precioMax;

  const handleSearchChange = useCallback(
    (value: string) => {
      setFilter('search', value);
      syncUrl();
    },
    [setFilter, syncUrl]
  );

  const handlePrecioMinChange = useCallback(
    (value: string) => {
      setFilter('precioMin', value);
      syncUrl();
    },
    [setFilter, syncUrl]
  );

  const handlePrecioMaxChange = useCallback(
    (value: string) => {
      setFilter('precioMax', value);
      syncUrl();
    },
    [setFilter, syncUrl]
  );

  const handleClearFilters = useCallback(() => {
    clearFilters();
    syncUrl();
  }, [clearFilters, syncUrl]);

  const handleSelectCategory = useCallback(
    (id: string | null) => {
      setFilter('categoriaId', id);
      syncUrl();
    },
    [setFilter, syncUrl]
  );

  const handlePageChange = useCallback(
    (page: number) => {
      setPage(page);
      syncUrl();
    },
    [setPage, syncUrl]
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 lg:text-3xl dark:text-gray-100">Catalogo de Productos</h1>
        <p className="mt-1 text-gray-500 dark:text-gray-400 dark:text-gray-400">Explora nuestros productos y encontra lo que buscas</p>
      </div>

      <div className="mb-6">
        <ProductFilters
          search={filters.search}
          precioMin={filters.precioMin}
          precioMax={filters.precioMax}
          onSearchChange={handleSearchChange}
          onPrecioMinChange={handlePrecioMinChange}
          onPrecioMaxChange={handlePrecioMaxChange}
          onClear={handleClearFilters}
          hasActiveFilters={hasActiveFilters}
        />
      </div>

      <div className="flex gap-8">
        <aside className="hidden w-64 shrink-0 lg:block">
          <CategoryNav
            categories={categories}
            isLoading={categoriesLoading}
            isError={categoriesError}
            error={categoriesErrorObj}
            selectedCategoryId={filters.categoriaId}
            onSelectCategory={handleSelectCategory}
            onRetry={() => refetchCategories()}
          />
        </aside>

        <div className="flex-1">
          <ProductGrid
            products={productData?.items}
            isLoading={productsLoading}
            isError={productsError}
            error={productsErrorObj}
            hasFilters={hasActiveFilters}
            onRetry={() => refetchProducts()}
            onClearFilters={handleClearFilters}
          />

          {productData && Math.ceil(productData.total / productData.limit) > 1 && (
            <PaginationBar
              currentPage={page}
              totalPages={Math.ceil(productData.total / productData.limit)}
              onPageChange={handlePageChange}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default CatalogPage;
