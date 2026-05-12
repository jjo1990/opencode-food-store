/**
 * Register Form - User registration form
 * Following FSD: features/auth/ directory
 */
import { useForm } from '@tanstack/react-form';
import { useAuthStore } from '../../stores/authStore';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

export function RegisterForm() {
  const navigate = useNavigate();
  const register = useAuthStore((state) => state.register);
  const isLoading = useAuthStore((state) => state.isLoading);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const form = useForm({
    defaultValues: {
      email: '',
      password: '',
      passwordConfirm: '',
      full_name: '',
    },
    onSubmit: async ({ value }) => {
      if (value.password !== value.passwordConfirm) {
        setSubmitError('Las contraseñas no coinciden');
        return;
      }

      setSubmitError(null);
      try {
        await register(value.email, value.password, value.full_name);
        navigate('/login');
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Registration failed';
        setSubmitError(message);
      }
    },
  });

  return (
    <form onSubmit={form.handleSubmit} className="auth-form">
      <h2>Crear Cuenta</h2>

      {submitError && <div className="error-message">{submitError}</div>}

      <div className="form-field">
        <label htmlFor="full_name">Nombre completo</label>
        <input
          id="full_name"
          type="text"
          {...form.register('full_name', {
            required: 'Nombre es requerido',
            minLength: { value: 2, message: 'Nombre muy corto' },
          })}
          placeholder="Juan Pérez"
        />
        {form.fieldMeta('full_name').isTouched && form.fieldMeta('full_name').error && (
          <span className="field-error">{form.fieldMeta('full_name').error}</span>
        )}
      </div>

      <div className="form-field">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          {...form.register('email', {
            required: 'Email es requerido',
            validate: (value) =>
              /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Email inválido',
          })}
          placeholder="tu@email.com"
        />
        {form.fieldMeta('email').isTouched && form.fieldMeta('email').error && (
          <span className="field-error">{form.fieldMeta('email').error}</span>
        )}
      </div>

      <div className="form-field">
        <label htmlFor="password">Contraseña</label>
        <input
          id="password"
          type="password"
          {...form.register('password', {
            required: 'Contraseña es requerida',
            minLength: { value: 8, message: 'La contraseña debe tener al menos 8 caracteres' },
          })}
          placeholder="••••••••"
        />
        {form.fieldMeta('password').isTouched && form.fieldMeta('password').error && (
          <span className="field-error">{form.fieldMeta('password').error}</span>
        )}
      </div>

      <div className="form-field">
        <label htmlFor="passwordConfirm">Confirmar contraseña</label>
        <input
          id="passwordConfirm"
          type="password"
          {...form.register('passwordConfirm', {
            required: 'Confirmar contraseña es requerido',
          })}
          placeholder="••••••••"
        />
        {form.fieldMeta('passwordConfirm').isTouched && form.fieldMeta('passwordConfirm').error && (
          <span className="field-error">{form.fieldMeta('passwordConfirm').error}</span>
        )}
      </div>

      <button type="submit" disabled={isLoading} className="submit-btn">
        {isLoading ? 'Creando cuenta...' : 'Crear Cuenta'}
      </button>

      <p className="form-footer">
        ¿Ya tienes cuenta? <a href="/login">Inicia sesión</a>
      </p>
    </form>
  );
}

export default RegisterForm;