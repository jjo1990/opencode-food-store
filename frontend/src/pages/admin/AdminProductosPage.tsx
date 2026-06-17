import { useState } from 'react';
import { useAdminProductos } from '../../features/admin-catalog/hooks/useAdminProductos';
import { Badge } from '../../shared/components/Badge';

export function AdminProductosPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [disponible, setDisponible] = useState<string>('');
  const [eliminado, setEliminado] = useState<string>('');

  const params = {
    page,
    size: 15,
    ...(search && { search }),
    ...(disponible !== '' && { disponible: disponible === 'true' }),
    ...(eliminado !== '' && { eliminado: eliminado === 'true' }),
  };

  const { data, isLoading, isError } = useAdminProductos(params);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Gestión de Productos</h1>
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          Administración completa del catálogo de productos, incluyendo elementos eliminados.
        </p>
      </div>

      <div className="mb-6 flex flex-wrap gap-4">
        <input
          type="text"
          placeholder="Buscar por nombre..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus-visible:border-indigo-500 focus:outline-none focus-visible:ring-1 focus-visible:ring-indigo-500"
        />
        <select
          value={disponible}
          onChange={(e) => {
            setDisponible(e.target.value);
            setPage(1);
          }}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus-visible:border-indigo-500 focus:outline-none focus-visible:ring-1 focus-visible:ring-indigo-500"
        >
          <option value="">Todos (disponibilidad)</option>
          <option value="true">Disponible</option>
          <option value="false">No disponible</option>
        </select>
        <select
          value={eliminado}
          onChange={(e) => {
            setEliminado(e.target.value);
            setPage(1);
          }}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus-visible:border-indigo-500 focus:outline-none focus-visible:ring-1 focus-visible:ring-indigo-500"
        >
          <option value="">Todos (estado)</option>
          <option value="false">Activos</option>
          <option value="true">Eliminados</option>
        </select>
      </div>

      {isLoading && <div className="py-12 text-center text-gray-500 dark:text-gray-400">Cargando productos...</div>}

      {isError && <div className="py-12 text-center text-red-500">Error al cargar productos.</div>}

      {data && (
        <>
          <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                    Nombre
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                    Precio
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                    Stock
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                    Disponible
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                    Estado
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                    Categorías
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-900">
                {data.items.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                      No se encontraron productos.
                    </td>
                  </tr>
                ) : (
                  data.items.map((item) => (
                    <tr
                      key={item.id}
                      className={item.eliminado ? 'bg-gray-50 dark:bg-gray-800 text-gray-500 dark:text-gray-400' : 'hover:bg-gray-50 dark:bg-gray-800'}
                    >
                      <td className="px-4 py-3 text-sm">
                        <span
                          className={item.eliminado ? 'line-through' : 'font-medium text-gray-900 dark:text-gray-100'}
                        >
                          {item.nombre}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
                        ${item.precio_base.toFixed(2)}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{item.stock_cantidad}</td>
                      <td className="px-4 py-3 text-center">
                        <Badge variant={item.disponible ? 'success' : 'error'} size="sm">
                          {item.disponible ? 'Sí' : 'No'}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <Badge variant={item.eliminado ? 'error' : 'success'} size="sm">
                          {item.eliminado ? 'Eliminado' : 'Activo'}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                        {item.categorias.length > 0 ? item.categorias.join(', ') : '—'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Mostrando {(page - 1) * 15 + 1}–{Math.min(page * 15, data.total)} de {data.total}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Anterior
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= data.pages}
                className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Siguiente
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default AdminProductosPage;
