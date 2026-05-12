/**
 * Login Form - User authentication form
 * Following FSD: features/auth/ directory
 */
import { useForm } from '@tanstack/react-form';
import { useAuthStore } from '../../stores/authStore';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

export function LoginForm() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const isLoading = useAuthStore((state) => state.isLoading);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const form = useForm({
    defaultValues: {
      email: '',
      password: '',
    },
    onSubmit: async ({ value }) => {
      setSubmitError(null);
      try {
        await login(value.email, value.password);
        navigate('/dashboard');
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Login failed';
        setSubmitError(message);
      }
    },
  });

  return (
    <form onSubmit={form.handleSubmit} className="auth-form">
      <h2>Iniciar Sesión</h2>

      {submitError && <div className="error-message">{submitError}</div>}

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
          })}
          placeholder="••••••••"
        />
        {form.fieldMeta('password').isTouched && form.fieldMeta('password').error && (
          <span className="field-error">{form.fieldMeta('password').error}</span>
        )}
      </div>

      <button type="submit" disabled={isLoading} className="submit-btn">
        {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
      </button>

      <p className="form-footer">
        ¿No tienes cuenta? <a href="/register">Regístrate</a>
      </p>
    </form>
  );
}

export default LoginForm;