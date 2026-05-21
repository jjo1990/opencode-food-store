import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {
  getAddresses,
  createAddress,
  updateAddress,
  deleteAddress,
  setPrincipalAddress,
} from '../../shared/api/direccionesApi';
import type {
  DireccionResponse,
  DireccionCreate,
  DireccionUpdate,
} from '../../shared/api/direccionesApi';
import type { Address } from './types';

function mapAddress(data: DireccionResponse): Address {
  return {
    id: data.id,
    usuario_id: data.usuario_id,
    alias: data.alias,
    calle: data.calle,
    numero: data.numero,
    piso: data.piso,
    departamento: data.departamento,
    ciudad: data.ciudad,
    codigo_postal: data.codigo_postal,
    referencia: data.referencia,
    es_principal: data.es_principal,
    created_at: data.created_at,
    updated_at: data.updated_at,
  };
}

export function useAddresses() {
  return useQuery<Address[]>({
    queryKey: ['addresses'],
    queryFn: async () => {
      const data = await getAddresses();
      return data.map(mapAddress);
    },
  });
}

export function useCreateAddress() {
  const queryClient = useQueryClient();
  return useMutation<Address, Error, DireccionCreate>({
    mutationFn: async (payload) => {
      const data = await createAddress(payload);
      return mapAddress(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['addresses'] });
      toast.success('Dirección creada correctamente');
    },
    onError: (error) => {
      toast.error(error.message || 'Error al crear dirección');
    },
  });
}

export function useUpdateAddress() {
  const queryClient = useQueryClient();
  return useMutation<Address, Error, { id: string; payload: DireccionUpdate }>({
    mutationFn: async ({ id, payload }) => {
      const data = await updateAddress(id, payload);
      return mapAddress(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['addresses'] });
      toast.success('Dirección actualizada correctamente');
    },
    onError: (error) => {
      toast.error(error.message || 'Error al actualizar dirección');
    },
  });
}

export function useDeleteAddress() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: deleteAddress,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['addresses'] });
      toast.success('Dirección eliminada correctamente');
    },
    onError: (error) => {
      toast.error(error.message || 'Error al eliminar dirección');
    },
  });
}

export function useSetPrincipal() {
  const queryClient = useQueryClient();
  return useMutation<Address, Error, string>({
    mutationFn: async (id) => {
      const data = await setPrincipalAddress(id);
      return mapAddress(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['addresses'] });
      toast.success('Dirección principal actualizada');
    },
    onError: (error) => {
      toast.error(error.message || 'Error al establecer dirección principal');
    },
  });
}
