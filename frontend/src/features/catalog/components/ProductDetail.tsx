import { Skeleton } from '../../../shared/components/Skeleton';
import { ErrorDisplay } from '../../../shared/components/ErrorDisplay';
import { Button } from '../../../shared/components/Button';
import type { Product } from '../../../entities/product/types';

interface ProductDetailProps {
  product: Product | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  onRetry: () => void;
  onAddToCart?: (product: Product) => void;
}

const formatPrice = (price: number) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(price);

export function ProductDetail({
  product,
  isLoading,
  isError,
  error,
  onRetry,
  onAddToCart,
}: ProductDetailProps) {
  if (isLoading) {
    return (
      <div className="grid gap-8 md:grid-cols-2">
        <Skeleton variant="card" className="h-96" />
        <div className="space-y-4">
          <Skeleton variant="text" width="60%" />
          <Skeleton variant="text" width="80%" />
          <Skeleton variant="text" width="30%" />
          <Skeleton variant="text" />
          <Skeleton variant="text" />
          <Skeleton variant="text" width="50%" />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorDisplay message={error?.message || 'Error al cargar el producto'} onRetry={onRetry} />
    );
  }

  if (!product) {
    return <ErrorDisplay message="Producto no encontrado" />;
  }

  return (
    <div className="grid gap-8 md:grid-cols-2">
      <div className="flex h-96 items-center justify-center overflow-hidden rounded-xl bg-gray-100">
        {product.imagenes && product.imagenes.length > 0 ? (
          <img
            src={product.imagenes[0].url}
            alt={product.nombre}
            className="h-full w-full object-cover"
          />
        ) : (
          <svg
            className="h-24 w-24 text-gray-300"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        )}
      </div>

      <div className="flex flex-col gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{product.nombre}</h1>
            <span
              className={`rounded-full px-3 py-0.5 text-xs font-medium ${
                product.disponible ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}
            >
              {product.disponible ? 'Disponible' : 'Agotado'}
            </span>
          </div>
          <p className="mt-1 text-sm text-gray-500">
            {product.categorias?.map((c) => c.nombre).join(', ')}
          </p>
        </div>

        <p className="text-3xl font-bold text-primary">{formatPrice(product.precio)}</p>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
            Descripción
          </h3>
          <p className="mt-1 text-gray-700">{product.descripcion}</p>
        </div>

        {product.ingredientes && product.ingredientes.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
              Ingredientes
            </h3>
            <div className="mt-2 flex flex-wrap gap-2">
              {product.ingredientes.map((ing) => (
                <span
                  key={ing.id}
                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                    ing.es_alergeno
                      ? 'bg-yellow-100 text-yellow-800 ring-1 ring-yellow-300'
                      : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {ing.nombre}
                  {ing.es_alergeno && (
                    <span className="ml-1" title="Alérgeno">
                      ⚠
                    </span>
                  )}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="mt-auto pt-4">
          <Button
            className="w-full"
            disabled={!product.disponible}
            onClick={() => onAddToCart?.(product)}
          >
            Agregar al carrito
          </Button>
        </div>
      </div>
    </div>
  );
}

export default ProductDetail;
