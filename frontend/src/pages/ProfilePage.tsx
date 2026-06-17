import { useState } from 'react';
import { ProfileForm } from '../features/profile/components/ProfileForm';
import { PasswordForm } from '../features/profile/components/PasswordForm';
import { Button } from '../shared/components/Button';
import { Card } from '../shared/components/Card';

export function ProfilePage() {
  const [isPasswordOpen, setIsPasswordOpen] = useState(false);

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="mb-8 text-2xl font-bold text-gray-900 dark:text-gray-100">Mi Perfil</h1>

      <div className="space-y-8">
        <ProfileForm />

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Contraseña</h2>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Cambiá tu contraseña periódicamente por seguridad
              </p>
            </div>
            <Button variant="secondary" onClick={() => setIsPasswordOpen(true)}>
              Cambiar contraseña
            </Button>
          </div>
        </Card>
      </div>

      <PasswordForm isOpen={isPasswordOpen} onClose={() => setIsPasswordOpen(false)} />
    </div>
  );
}

export default ProfilePage;
