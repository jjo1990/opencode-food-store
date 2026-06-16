import { useState } from 'react';
import { useAdminProductos } from '../../features/admin-catalog/hooks/useAdminProductos';

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
        <h1 className="text-3xl font-bold text-gray-900">Gestión de Productos</h1>
        <p className="mt-2 text-sm text-gray-500">
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
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        <select
          value={disponible}
          onChange={(e) => {
            setDisponible(e.target.value);
            setPage(1);
          }}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
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
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="">Todos (estado)</option>
          <option value="false">Activos</option>
          <option value="true">Eliminados</option>
        </select>
      </div>

      {isLoading && <div className="py-12 text-center text-gray-500">Cargando productos...</div>}

      {isError && <div className="py-12 text-center text-red-500">Error al cargar productos.</div>}

      {data && (
        <>
          <div className="overflow-x-auto rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Nombre
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Precio
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Stock
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500">
                    Disponible
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500">
                    Estado
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Categorías
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {data.items.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                      No se encontraron productos.
                    </td>
                  </tr>
                ) : (
                  data.items.map((item) => (
                    <tr
                      key={item.id}
                      className={item.eliminado ? 'bg-gray-50 text-gray-400' : 'hover:bg-gray-50'}
                    >
                      <td className="px-4 py-3 text-sm">
                        <span
                          className={item.eliminado ? 'line-through' : 'font-medium text-gray-900'}
                        >
                          {item.nombre}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        ${item.precio_base.toFixed(2)}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">{item.stock_cantidad}</td>
                      <td className="px-4 py-3 text-center">
                        <span
                          className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                            item.disponible
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {item.disponible ? 'Sí' : 'No'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span
                          className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                            item.eliminado
                              ? 'bg-red-100 text-red-800'
                              : 'bg-green-100 text-green-800'
                          }`}
                        >
                          {item.eliminado ? 'Eliminado' : 'Activo'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {item.categorias.length > 0 ? item.categorias.join(', ') : '—'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Mostrando {(page - 1) * 15 + 1}–{Math.min(page * 15, data.total)} de {data.total}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Anterior
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= data.pages}
                className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
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
