import { useDashboardStore } from '../../../stores/dashboardStore';

const GRANULARIDAD_OPTIONS: { label: string; value: 'day' | 'week' | 'month' }[] = [
  { label: 'Día', value: 'day' },
  { label: 'Semana', value: 'week' },
  { label: 'Mes', value: 'month' },
];

export function DashboardFilters() {
  const filters = useDashboardStore((s) => s.filters);
  const setDateRange = useDashboardStore((s) => s.setDateRange);
  const setGranularidad = useDashboardStore((s) => s.setGranularidad);

  return (
    <div className="mb-6 flex flex-wrap items-end gap-4">
      <div>
        <label htmlFor="fecha-inicio" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Desde
        </label>
        <input
          id="fecha-inicio"
          type="date"
          value={filters.fechaInicio}
          onChange={(e) => setDateRange(e.target.value, filters.fechaFin)}
          className="mt-1 block rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus-visible:border-primary focus:outline-none focus-visible:ring-1 focus-visible:ring-primary dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
        />
      </div>
      <div>
        <label htmlFor="fecha-fin" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Hasta
        </label>
        <input
          id="fecha-fin"
          type="date"
          value={filters.fechaFin}
          onChange={(e) => setDateRange(filters.fechaInicio, e.target.value)}
          className="mt-1 block rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus-visible:border-primary focus:outline-none focus-visible:ring-1 focus-visible:ring-primary dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
        />
      </div>
      <div>
        <span className="block text-sm font-medium text-gray-700 dark:text-gray-300">Granularidad</span>
        <div className="mt-1 inline-flex rounded-lg border border-gray-300 bg-white dark:border-gray-600 dark:bg-gray-800">
          {GRANULARIDAD_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setGranularidad(opt.value)}
              className={`px-3 py-2 text-sm font-medium transition-colors first:rounded-l-lg last:rounded-r-lg ${
                filters.granularidad === opt.value
                  ? 'bg-primary text-white'
                  : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default DashboardFilters;
