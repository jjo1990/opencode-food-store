import type { Address } from '../../../entities/address/types';
import { Button } from '../../../shared/components/Button';
import { Card } from '../../../shared/components/Card';

interface AddressCardProps {
  address: Address;
  onEdit: (address: Address) => void;
  onDelete: (address: Address) => void;
  onSetPrincipal: (id: string) => void;
}

export function AddressCard({ address, onEdit, onDelete, onSetPrincipal }: AddressCardProps) {
  return (
    <Card className="relative">
      {address.es_principal && (
        <span className="absolute right-3 top-3 rounded-full bg-primary-100 px-2.5 py-0.5 text-xs font-medium text-primary-800">
          Principal
        </span>
      )}

      <div className="space-y-2">
        {address.alias && <h3 className="font-semibold text-gray-900 dark:text-gray-100">{address.alias}</h3>}
        <p className="text-sm text-gray-700 dark:text-gray-300">
          {address.calle} {address.numero}
          {address.piso && `, Piso ${address.piso}`}
          {address.departamento && `, Dto. ${address.departamento}`}
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {address.ciudad}, CP {address.codigo_postal}
        </p>
        {address.referencia && <p className="text-xs text-gray-500 dark:text-gray-400">Ref: {address.referencia}</p>}
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <Button variant="secondary" onClick={() => onEdit(address)}>
          Editar
        </Button>
        {!address.es_principal && (
          <Button variant="ghost" onClick={() => onSetPrincipal(address.id)}>
            Establecer como principal
          </Button>
        )}
        <Button variant="danger" onClick={() => onDelete(address)}>
          Eliminar
        </Button>
      </div>
    </Card>
  );
}

export default AddressCard;
