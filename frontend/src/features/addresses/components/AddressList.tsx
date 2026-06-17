import { useAddresses } from '../../../entities/address/api';
import { AddressCard } from './AddressCard';
import { Skeleton } from '../../../shared/components/Skeleton';
import { ErrorDisplay } from '../../../shared/components/ErrorDisplay';
import { EmptyState } from '../../../shared/components/EmptyState';
import { Button } from '../../../shared/components/Button';
import type { Address } from '../../../entities/address/types';

interface AddressListProps {
  onEdit: (address: Address) => void;
  onDelete: (address: Address) => void;
  onSetPrincipal: (id: string) => void;
  onAdd: () => void;
}

export function AddressList({ onEdit, onDelete, onSetPrincipal, onAdd }: AddressListProps) {
  const { data: addresses, isLoading, isError, error, refetch } = useAddresses();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="overflow-hidden rounded-xl bg-white shadow-md dark:bg-gray-800 dark:shadow-gray-900/30 p-6">
            <Skeleton variant="text" width="50%" />
            <div className="mt-3 space-y-2">
              <Skeleton variant="text" width="80%" />
              <Skeleton variant="text" width="60%" />
            </div>
            <div className="mt-4 flex gap-2">
              <Skeleton variant="text" width="60px" />
              <Skeleton variant="text" width="60px" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorDisplay
        message={error?.message || 'Error al cargar las direcciones'}
        onRetry={refetch}
      />
    );
  }

  if (!addresses || addresses.length === 0) {
    return (
      <div className="space-y-6">
        <EmptyState
          title="Aún no tenés direcciones guardadas"
          description="Agregá una dirección para recibir tus pedidos."
          action={{ label: 'Agregar dirección', onClick: onAdd }}
        />
      </div>
    );
  }

  const sorted = [...addresses].sort((a, b) => {
    if (a.es_principal) return -1;
    if (b.es_principal) return 1;
    return 0;
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <Button onClick={onAdd}>Agregar dirección</Button>
      </div>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {sorted.map((address) => (
          <AddressCard
            key={address.id}
            address={address}
            onEdit={onEdit}
            onDelete={onDelete}
            onSetPrincipal={onSetPrincipal}
          />
        ))}
      </div>
    </div>
  );
}

export default AddressList;
