import { useState, useEffect } from 'react';
import { useAdminConfig, useUpdateConfig } from '../../features/admin-config/hooks/useAdminConfig';
import { ErrorDisplay } from '../../shared/components/ErrorDisplay';
import { EmptyState } from '../../shared/components/EmptyState';
import { Skeleton } from '../../shared/components/Skeleton';
import { Spinner } from '../../shared/components/Spinner';

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '—';
  try {
    return new Date(dateStr).toLocaleString('es-AR');
  } catch {
    return dateStr;
  }
}

export function AdminConfigPage() {
  const { data, isLoading, isError, error, refetch } = useAdminConfig();
  const updateMutation = useUpdateConfig();
  const [values, setValues] = useState<Record<string, string>>({});

  useEffect(() => {
    if (data?.configuracion) {
      setValues({ ...data.configuracion });
    }
  }, [data]);

  const keys = Object.keys(values);

  const handleChange = (key: string, value: string) => {
    setValues((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    updateMutation.mutate({ configuracion: values });
  };

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="space-y-6">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i}>
              <Skeleton width="120px" height="14px" className="mb-2" />
              <Skeleton height="42px" className="rounded-lg" />
            </div>
          ))}
        </div>
      );
    }

    if (isError) {
      return (
        <ErrorDisplay
          message={(error as Error)?.message || 'Error al cargar la configuración'}
          onRetry={() => refetch()}
        />
      );
    }

    if (keys.length === 0) {
      return (
        <EmptyState
          title="Sin parámetros configurados"
          description="No hay parámetros de configuración disponibles en el sistema."
        />
      );
    }

    const auditoria = data?.auditoria ?? {};

    return (
      <div className="space-y-6">
        {Object.entries(values).map(([key, value]) => {
          const audit = auditoria[key];
          const isMensaje = key === 'mensaje_bienvenida';
          return (
            <div key={key}>
              <label className="mb-1 block text-sm font-medium capitalize text-gray-700 dark:text-gray-300">
                {key.replace(/_/g, ' ')}
              </label>
              {isMensaje ? (
                <textarea
                  value={value}
                  onChange={(e) => handleChange(key, e.target.value)}
                  rows={3}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-700 px-3 py-2 text-sm focus-visible:border-primary focus:outline-none focus-visible:ring-1 focus-visible:ring-primary"
                />
              ) : (
                <input
                  type="text"
                  value={value}
                  onChange={(e) => handleChange(key, e.target.value)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-700 px-3 py-2 text-sm focus-visible:border-primary focus:outline-none focus-visible:ring-1 focus-visible:ring-primary"
                />
              )}
              {audit && (
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  Última modificación: {audit.updated_by_name || 'Sistema'} el{' '}
                  {formatDate(audit.updated_at)}
                </p>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Configuración</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Parámetros del sistema</p>
        </div>
        {keys.length > 0 && !isLoading && !isError && (
          <button
            onClick={handleSave}
            disabled={updateMutation.isPending}
            className="rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-primary-600 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {updateMutation.isPending ? (
              <span className="flex items-center gap-2">
                <Spinner size="sm" />
                Guardando...
              </span>
            ) : (
              'Guardar cambios'
            )}
          </button>
        )}
      </div>

      <div className="rounded-xl bg-white dark:bg-gray-900 shadow-sm dark:shadow-gray-900/30 border border-gray-200 dark:border-gray-700 p-6">
        {renderContent()}
      </div>
    </div>
  );
}

export default AdminConfigPage;
