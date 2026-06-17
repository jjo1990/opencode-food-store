import { useState } from 'react';
import { useAdminCategorias } from '../../features/admin-catalog/hooks/useAdminCategorias';
import { Badge } from '../../shared/components/Badge';
import type { AdminCategoriaListItem } from '../../shared/api/adminCatalogApi';

interface CategoriaNode extends AdminCategoriaListItem {
  children: CategoriaNode[];
}

function buildTree(items: AdminCategoriaListItem[]): CategoriaNode[] {
  const map = new Map<string, CategoriaNode>();
  const roots: CategoriaNode[] = [];

  for (const item of items) {
    map.set(item.id, { ...item, children: [] });
  }

  for (const item of items) {
    const node = map.get(item.id)!;
    if (item.parent_id && map.has(item.parent_id)) {
      map.get(item.parent_id)!.children.push(node);
    } else {
      roots.push(node);
    }
  }

  return roots;
}

export function AdminCategoriasPage() {
  const [eliminado, setEliminado] = useState<string>('');

  const filterEliminado: boolean | undefined = eliminado !== '' ? eliminado === 'true' : undefined;
  const { data, isLoading, isError } = useAdminCategorias(filterEliminado);

  const tree = data ? buildTree(data.items) : [];

  const renderTree = (items: CategoriaNode[], level: number = 0): React.ReactNode[] => {
    return items.flatMap((item) => {
      const childNodes = item.children?.length ? renderTree(item.children, level + 1) : [];
      return [
        <tr
          key={item.id}
          className={item.eliminado ? 'bg-gray-50 dark:bg-gray-800 text-gray-500 dark:text-gray-400' : 'hover:bg-gray-50 dark:bg-gray-800'}
        >
          <td className="px-4 py-3 text-sm">
            <span
              className={item.eliminado ? 'line-through' : 'font-medium text-gray-900 dark:text-gray-100'}
              style={{ paddingLeft: `${level * 1.5}rem` }}
            >
              {level > 0 && '└ '}
              {item.nombre}
            </span>
          </td>
          <td className="px-4 py-3 text-center">
            <Badge variant={item.eliminado ? 'error' : 'success'} size="sm">
              {item.eliminado ? 'Eliminada' : 'Activa'}
            </Badge>
          </td>
          <td className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
            {item.created_at ? new Date(item.created_at).toLocaleDateString() : '—'}
          </td>
        </tr>,
        ...childNodes,
      ];
    });
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Gestión de Categorías</h1>
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          Administración de categorías jerárquicas, incluyendo elementos eliminados.
        </p>
      </div>

      <div className="mb-6">
        <select
          value={eliminado}
          onChange={(e) => setEliminado(e.target.value)}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus-visible:border-indigo-500 focus:outline-none focus-visible:ring-1 focus-visible:ring-indigo-500"
        >
          <option value="">Todas</option>
          <option value="false">Activas</option>
          <option value="true">Eliminadas</option>
        </select>
      </div>

      {isLoading && <div className="py-12 text-center text-gray-500 dark:text-gray-400">Cargando categorías...</div>}

      {isError && <div className="py-12 text-center text-red-500">Error al cargar categorías.</div>}

      {data && (
        <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                  Nombre
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                  Estado
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                  Creada
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-900">
              {data.items.length === 0 ? (
                <tr>
                  <td colSpan={3} className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                    No se encontraron categorías.
                  </td>
                </tr>
              ) : (
                renderTree(tree)
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default AdminCategoriasPage;
