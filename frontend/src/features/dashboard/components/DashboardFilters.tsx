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
        <label htmlFor="fecha-inicio" className="block text-sm font-medium text-gray-700">
          Desde
        </label>
        <input
          id="fecha-inicio"
          type="date"
          value={filters.fechaInicio}
          onChange={(e) => setDateRange(e.target.value, filters.fechaFin)}
          className="mt-1 block rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
        />
      </div>
      <div>
        <label htmlFor="fecha-fin" className="block text-sm font-medium text-gray-700">
          Hasta
        </label>
        <input
          id="fecha-fin"
          type="date"
          value={filters.fechaFin}
          onChange={(e) => setDateRange(filters.fechaInicio, e.target.value)}
          className="mt-1 block rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
        />
      </div>
      <div>
        <span className="block text-sm font-medium text-gray-700">Granularidad</span>
        <div className="mt-1 inline-flex rounded-lg border border-gray-300 bg-white">
          {GRANULARIDAD_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setGranularidad(opt.value)}
              className={`px-3 py-2 text-sm font-medium transition-colors first:rounded-l-lg last:rounded-r-lg ${
                filters.granularidad === opt.value
                  ? 'bg-primary text-white'
                  : 'text-gray-600 hover:bg-gray-100'
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
