import { create } from 'zustand';

function getDefaultFechaInicio(): string {
  const d = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  return d.toISOString().split('T')[0];
}

function getDefaultFechaFin(): string {
  return new Date().toISOString().split('T')[0];
}

interface DashboardFilters {
  fechaInicio: string;
  fechaFin: string;
  granularidad: 'day' | 'week' | 'month';
}

interface DashboardState {
  filters: DashboardFilters;
  setDateRange: (inicio: string, fin: string) => void;
  setGranularidad: (g: 'day' | 'week' | 'month') => void;
}

export const useDashboardStore = create<DashboardState>()((set) => ({
  filters: {
    fechaInicio: getDefaultFechaInicio(),
    fechaFin: getDefaultFechaFin(),
    granularidad: 'day',
  },
  setDateRange: (inicio, fin) =>
    set((state) => ({
      filters: { ...state.filters, fechaInicio: inicio, fechaFin: fin },
    })),
  setGranularidad: (g) =>
    set((state) => ({
      filters: { ...state.filters, granularidad: g },
    })),
}));
