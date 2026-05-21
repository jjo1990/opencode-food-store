import { useState } from 'react';
import {
  useCreateAddress,
  useUpdateAddress,
  useDeleteAddress,
  useSetPrincipal,
} from '../entities/address/api';
import { AddressList } from '../features/addresses/components/AddressList';
import { AddressForm } from '../features/addresses/components/AddressForm';
import { Modal } from '../shared/components/Modal';
import { Button } from '../shared/components/Button';
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
      <h1 className="mb-8 text-2xl font-bold text-gray-900">Mis Direcciones</h1>

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

      <Modal
        isOpen={!!deletingAddress}
        onClose={() => setDeletingAddress(null)}
        title="Eliminar dirección"
        footer={
          <div className="flex gap-3">
            <Button variant="ghost" onClick={() => setDeletingAddress(null)}>
              Cancelar
            </Button>
            <Button
              variant="danger"
              onClick={handleDeleteConfirm}
              isLoading={deleteMutation.isPending}
            >
              Eliminar
            </Button>
          </div>
        }
      >
        <p className="text-sm text-gray-600">
          ¿Estás seguro de que querés eliminar esta dirección? Esta acción no se puede deshacer.
        </p>
      </Modal>
    </div>
  );
}

export default AddressesPage;
