import { useState, useEffect, useCallback } from 'react';
import { Input } from '../../../shared/components/Input';
import { Button } from '../../../shared/components/Button';

interface ProductFiltersProps {
  search: string;
  precioMin: string;
  precioMax: string;
  onSearchChange: (value: string) => void;
  onPrecioMinChange: (value: string) => void;
  onPrecioMaxChange: (value: string) => void;
  onClear: () => void;
  hasActiveFilters: boolean;
}

export function ProductFilters({
  search,
  precioMin,
  precioMax,
  onSearchChange,
  onPrecioMinChange,
  onPrecioMaxChange,
  onClear,
  hasActiveFilters,
}: ProductFiltersProps) {
  const [localSearch, setLocalSearch] = useState(search);

  useEffect(() => {
    setLocalSearch(search);
  }, [search]);

  const debouncedSearch = useCallback(
    (() => {
      let timer: ReturnType<typeof setTimeout>;
      return (value: string) => {
        clearTimeout(timer);
        timer = setTimeout(() => onSearchChange(value), 300);
      };
    })(),
    [onSearchChange]
  );

  return (
    <div className="flex flex-wrap items-end gap-4">
      <div className="min-w-[200px] flex-1">
        <Input
          label="Buscar"
          placeholder="Buscar productos..."
          value={localSearch}
          onChange={(e) => {
            setLocalSearch(e.target.value);
            debouncedSearch(e.target.value);
          }}
        />
      </div>

      <div className="w-28">
        <Input
          label="Precio mín."
          type="number"
          placeholder="0"
          value={precioMin}
          onChange={(e) => onPrecioMinChange(e.target.value)}
        />
      </div>

      <div className="w-28">
        <Input
          label="Precio máx."
          type="number"
          placeholder="99999"
          value={precioMax}
          onChange={(e) => onPrecioMaxChange(e.target.value)}
        />
      </div>

      {hasActiveFilters && (
        <Button variant="ghost" onClick={onClear}>
          Limpiar filtros
        </Button>
      )}
    </div>
  );
}

export default ProductFilters;
