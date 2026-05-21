import { useState, useEffect } from 'react';
import { useProfile, useUpdateProfile } from '../../../entities/user/api';
import { Button } from '../../../shared/components/Button';
import { Input } from '../../../shared/components/Input';
import { Skeleton } from '../../../shared/components/Skeleton';
import { ErrorDisplay } from '../../../shared/components/ErrorDisplay';
import { Card } from '../../../shared/components/Card';

export function ProfileForm() {
  const { data: profile, isLoading, isError, error, refetch } = useProfile();
  const updateMutation = useUpdateProfile();

  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState('');
  const [telefono, setTelefono] = useState('');

  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name || '');
      setTelefono(profile.telefono || '');
    }
  }, [profile]);

  if (isLoading) {
    return (
      <Card>
        <div className="space-y-4">
          <Skeleton variant="text" width="40%" />
          <Skeleton variant="text" width="60%" />
          <Skeleton variant="text" width="50%" />
        </div>
      </Card>
    );
  }

  if (isError) {
    return (
      <ErrorDisplay message={error?.message || 'Error al cargar el perfil'} onRetry={refetch} />
    );
  }

  if (!profile) return null;

  const handleSave = () => {
    updateMutation.mutate(
      { full_name: fullName || null, telefono: telefono || null },
      {
        onSuccess: () => setIsEditing(false),
      }
    );
  };

  const handleCancel = () => {
    setFullName(profile.full_name || '');
    setTelefono(profile.telefono || '');
    setIsEditing(false);
  };

  const formatDate = (dateStr: string) =>
    new Intl.DateTimeFormat('es-AR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(new Date(dateStr));

  return (
    <Card>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Información personal</h2>
        {!isEditing && (
          <Button variant="ghost" onClick={() => setIsEditing(true)}>
            Editar
          </Button>
        )}
      </div>

      {isEditing ? (
        <div className="space-y-4">
          <Input label="Email" value={profile.email} disabled />
          <Input
            label="Nombre completo"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Tu nombre completo"
          />
          <Input
            label="Teléfono"
            value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
            placeholder="+54 11 1234-5678"
          />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="ghost" onClick={handleCancel}>
              Cancelar
            </Button>
            <Button onClick={handleSave} isLoading={updateMutation.isPending}>
              Guardar
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-500">Email</p>
            <p className="text-gray-900">{profile.email}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Nombre completo</p>
            <p className="text-gray-900">{profile.full_name || '—'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Teléfono</p>
            <p className="text-gray-900">{profile.telefono || '—'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Miembro desde</p>
            <p className="text-gray-900">{formatDate(profile.created_at)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Roles</p>
            <p className="text-gray-900">{profile.roles.join(', ')}</p>
          </div>
        </div>
      )}
    </Card>
  );
}

export default ProfileForm;
