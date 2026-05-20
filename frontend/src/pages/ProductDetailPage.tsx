import { useParams, Link } from 'react-router-dom';
import { useProduct } from '../entities/product/api';
import { ProductDetail } from '../features/catalog/components/ProductDetail';

export function ProductDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { data: product, isLoading, isError, error, refetch } = useProduct(slug || '');

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6">
        <Link
          to="/catalog"
          className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-primary"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Volver al catálogo
        </Link>
      </div>

      <ProductDetail
        product={product}
        isLoading={isLoading}
        isError={isError}
        error={error}
        onRetry={() => refetch()}
      />
    </div>
  );
}

export default ProductDetailPage;
