import { Link } from 'react-router-dom';
import type { Product } from '../../../entities/product/types';

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  const formatPrice = (price: number) =>
    new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(price);

  return (
    <Link
      to={`/catalog/${product.id}`}
      className="group flex flex-col overflow-hidden rounded-xl bg-white shadow-md transition-shadow hover:shadow-lg dark:bg-gray-800 dark:shadow-gray-900/30 dark:hover:shadow-gray-900/50"
    >
      <div className="relative flex h-48 items-center justify-center bg-gray-100 dark:bg-gray-700">
        {product.imagen_url ? (
          <img
            src={product.imagen_url}
            alt={product.nombre}
            className="h-full w-full object-cover"
          />
        ) : (
          <svg
            className="h-16 w-16 text-gray-300 dark:text-gray-600"
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
        <span
          className={`absolute right-2 top-2 rounded-full px-2.5 py-0.5 text-xs font-medium ${
            product.disponible ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
          }`}
        >
          {product.disponible ? 'Disponible' : 'Agotado'}
        </span>
      </div>

      <div className="flex flex-1 flex-col justify-between p-4">
        <h3 className="text-sm font-semibold text-gray-900 group-hover:text-primary dark:text-gray-100 dark:group-hover:text-primary-400">
          {product.nombre}
        </h3>
        <p className="mt-2 text-lg font-bold text-primary-700 dark:text-primary-400">{formatPrice(product.precio_base)}</p>
      </div>
    </Link>
  );
}

export default ProductCard;
