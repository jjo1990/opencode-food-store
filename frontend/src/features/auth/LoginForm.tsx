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

  const Field = form.Field;

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        e.stopPropagation();
        form.handleSubmit();
      }}
      className="auth-form"
    >
      <h2>Iniciar Sesión</h2>

      {submitError && <div className="error-message">{submitError}</div>}

      <Field
        name="email"
        validators={{
          onChange: ({ value }) =>
            !value
              ? 'Email es requerido'
              : !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
                ? 'Email inválido'
                : undefined,
        }}
      >
        {(field) => (
          <div className="form-field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
              placeholder="tu@email.com"
            />
            {field.state.meta.isTouched && field.state.meta.errors.length > 0 && (
              <span className="field-error">{field.state.meta.errors.join(', ')}</span>
            )}
          </div>
        )}
      </Field>

      <Field
        name="password"
        validators={{
          onChange: ({ value }) => (!value ? 'Contraseña es requerida' : undefined),
        }}
      >
        {(field) => (
          <div className="form-field">
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              type="password"
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
              placeholder="••••••••"
            />
            {field.state.meta.isTouched && field.state.meta.errors.length > 0 && (
              <span className="field-error">{field.state.meta.errors.join(', ')}</span>
            )}
          </div>
        )}
      </Field>

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
