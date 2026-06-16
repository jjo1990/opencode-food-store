import { useState } from 'react';
import { useAdminIngredientes } from '../../features/admin-catalog/hooks/useAdminIngredientes';

export function AdminIngredientesPage() {
  const [page, setPage] = useState(1);
  const [esAlergeno, setEsAlergeno] = useState<string>('');
  const [eliminado, setEliminado] = useState<string>('');

  const params = {
    page,
    size: 15,
    ...(esAlergeno !== '' && { es_alergeno: esAlergeno === 'true' }),
    ...(eliminado !== '' && { eliminado: eliminado === 'true' }),
  };

  const { data, isLoading, isError } = useAdminIngredientes(params);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Gestión de Ingredientes</h1>
        <p className="mt-2 text-sm text-gray-500">
          Administración del catálogo de ingredientes y alérgenos, incluyendo elementos eliminados.
        </p>
      </div>

      <div className="mb-6 flex flex-wrap gap-4">
        <select
          value={esAlergeno}
          onChange={(e) => {
            setEsAlergeno(e.target.value);
            setPage(1);
          }}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="">Todos (alérgeno)</option>
          <option value="true">Es alérgeno</option>
          <option value="false">No alérgeno</option>
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

      {isLoading && <div className="py-12 text-center text-gray-500">Cargando ingredientes...</div>}

      {isError && (
        <div className="py-12 text-center text-red-500">Error al cargar ingredientes.</div>
      )}

      {data && (
        <>
          <div className="overflow-x-auto rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Nombre
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500">
                    Alérgeno
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500">
                    Estado
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Creado
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {data.items.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                      No se encontraron ingredientes.
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
                      <td className="px-4 py-3 text-center">
                        <span
                          className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                            item.es_alergeno
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-gray-100 text-gray-600'
                          }`}
                        >
                          {item.es_alergeno ? '⚠ Alérgeno' : 'No'}
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
                        {item.created_at ? new Date(item.created_at).toLocaleDateString() : '—'}
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

export default AdminIngredientesPage;
