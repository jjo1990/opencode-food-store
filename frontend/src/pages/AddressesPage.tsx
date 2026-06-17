import { useState } from 'react';
import {
  useCreateAddress,
  useUpdateAddress,
  useDeleteAddress,
  useSetPrincipal,
} from '../entities/address/api';
import { AddressList } from '../features/addresses/components/AddressList';
import { AddressForm } from '../features/addresses/components/AddressForm';
import { ConfirmationModal } from '../shared/components/ConfirmationModal';
import type { Address } from '../entities/address/types';
import type { DireccionCreate, DireccionUpdate } from '../shared/api/direccionesApi';

export function AddressesPage() {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingAddress, setEditingAddress] = useState<Address | null>(null);
  const [deletingAddress, setDeletingAddress] = useState<Address | null>(null);

  const createMutation = useCreateAddress();
  const updateMutation = useUpdateAddress();
  const deleteMutation = useDeleteAddress();
  const setPrincipalMutation = useSetPrincipal();

  const handleOpenCreate = () => {
    setEditingAddress(null);
    setIsFormOpen(true);
  };

  const handleOpenEdit = (address: Address) => {
    setEditingAddress(address);
    setIsFormOpen(true);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setEditingAddress(null);
  };

  const handleSubmitForm = (payload: DireccionCreate | DireccionUpdate) => {
    if (editingAddress) {
      updateMutation.mutate({ id: editingAddress.id, payload }, { onSuccess: handleCloseForm });
    } else {
      createMutation.mutate(payload as DireccionCreate, {
        onSuccess: handleCloseForm,
      });
    }
  };

  const handleDeleteConfirm = () => {
    if (!deletingAddress) return;
    deleteMutation.mutate(deletingAddress.id, {
      onSuccess: () => setDeletingAddress(null),
    });
  };

  const isFormLoading = createMutation.isPending || updateMutation.isPending;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="mb-8 text-2xl font-bold text-gray-900 dark:text-gray-100">Mis Direcciones</h1>

      <AddressList
        onEdit={handleOpenEdit}
        onDelete={setDeletingAddress}
        onSetPrincipal={(id) => setPrincipalMutation.mutate(id)}
        onAdd={handleOpenCreate}
      />

      <AddressForm
        isOpen={isFormOpen}
        onClose={handleCloseForm}
        address={editingAddress}
        onSubmit={handleSubmitForm}
        isLoading={isFormLoading}
      />

      <ConfirmationModal
        isOpen={!!deletingAddress}
        onClose={() => setDeletingAddress(null)}
        onConfirm={handleDeleteConfirm}
        title="Eliminar dirección"
        message="¿Estás seguro de que querés eliminar esta dirección? Esta acción no se puede deshacer."
        variant="danger"
        confirmLabel="Eliminar"
        isLoading={deleteMutation.isPending}
      />
    </div>
  );
}

export default AddressesPage;
