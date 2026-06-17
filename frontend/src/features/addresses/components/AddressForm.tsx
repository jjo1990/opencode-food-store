import { useState, useEffect } from 'react';
import { Modal } from '../../../shared/components/Modal';
import { Input } from '../../../shared/components/Input';
import { Button } from '../../../shared/components/Button';
import type { Address } from '../../../entities/address/types';
import type { DireccionCreate, DireccionUpdate } from '../../../shared/api/direccionesApi';

interface AddressFormProps {
  isOpen: boolean;
  onClose: () => void;
  address?: Address | null;
  onSubmit: (payload: DireccionCreate | DireccionUpdate) => void;
  isLoading?: boolean;
}

export function AddressForm({ isOpen, onClose, address, onSubmit, isLoading }: AddressFormProps) {
  const [alias, setAlias] = useState('');
  const [calle, setCalle] = useState('');
  const [numero, setNumero] = useState('');
  const [piso, setPiso] = useState('');
  const [departamento, setDepartamento] = useState('');
  const [ciudad, setCiudad] = useState('');
  const [codigoPostal, setCodigoPostal] = useState('');
  const [referencia, setReferencia] = useState('');
  const [esPrincipal, setEsPrincipal] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const isEditing = !!address;

  useEffect(() => {
    if (address) {
      setAlias(address.alias || '');
      setCalle(address.calle);
      setNumero(address.numero);
      setPiso(address.piso || '');
      setDepartamento(address.departamento || '');
      setCiudad(address.ciudad);
      setCodigoPostal(address.codigo_postal);
      setReferencia(address.referencia || '');
      setEsPrincipal(address.es_principal);
    } else {
      setAlias('');
      setCalle('');
      setNumero('');
      setPiso('');
      setDepartamento('');
      setCiudad('');
      setCodigoPostal('');
      setReferencia('');
      setEsPrincipal(false);
    }
    setErrors({});
  }, [address, isOpen]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!calle.trim()) newErrors.calle = 'La calle es requerida';
    if (!numero.trim()) newErrors.numero = 'El número es requerido';
    if (!ciudad.trim()) newErrors.ciudad = 'La ciudad es requerida';
    if (!codigoPostal.trim()) newErrors.codigoPostal = 'El código postal es requerido';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validate()) return;

    const payload: DireccionCreate = {
      alias: alias || null,
      calle: calle.trim(),
      numero: numero.trim(),
      piso: piso || null,
      departamento: departamento || null,
      ciudad: ciudad.trim(),
      codigo_postal: codigoPostal.trim(),
      referencia: referencia || null,
      es_principal: esPrincipal,
    };

    onSubmit(payload);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar dirección' : 'Nueva dirección'}
      footer={
        <div className="flex gap-3">
          <Button variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit} isLoading={isLoading}>
            {isEditing ? 'Actualizar' : 'Guardar'}
          </Button>
        </div>
      }
    >
      <div className="space-y-4">
        <Input
          label="Alias"
          value={alias}
          onChange={(e) => setAlias(e.target.value)}
          placeholder="Ej: Casa, Trabajo"
        />
        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-2">
            <Input
              label="Calle"
              value={calle}
              onChange={(e) => setCalle(e.target.value)}
              error={errors.calle}
              placeholder="Av. Siempre Viva"
            />
          </div>
          <Input
            label="Número"
            value={numero}
            onChange={(e) => setNumero(e.target.value)}
            error={errors.numero}
            placeholder="123"
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Input
            label="Piso"
            value={piso}
            onChange={(e) => setPiso(e.target.value)}
            placeholder="3"
          />
          <Input
            label="Departamento"
            value={departamento}
            onChange={(e) => setDepartamento(e.target.value)}
            placeholder="A"
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Input
            label="Ciudad"
            value={ciudad}
            onChange={(e) => setCiudad(e.target.value)}
            error={errors.ciudad}
            placeholder="Buenos Aires"
          />
          <Input
            label="Código postal"
            value={codigoPostal}
            onChange={(e) => setCodigoPostal(e.target.value)}
            error={errors.codigoPostal}
            placeholder="C1425"
          />
        </div>
        <Input
          label="Referencia"
          value={referencia}
          onChange={(e) => setReferencia(e.target.value)}
          placeholder="Cerca de la plaza"
        />
        <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <input
            type="checkbox"
            checked={esPrincipal}
            onChange={(e) => setEsPrincipal(e.target.checked)}
            className="rounded border-gray-300 dark:border-gray-600 text-primary focus-visible:ring-primary"
          />
          Establecer como dirección principal
        </label>
      </div>
    </Modal>
  );
}

export default AddressForm;
