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
      <h2 className="dark:text-gray-100">Crear Cuenta</h2>

      {submitError && <div className="error-message">{submitError}</div>}

      <Field
        name="full_name"
        validators={{
          onChange: ({ value }) =>
            !value ? 'Nombre es requerido' : value.length < 2 ? 'Nombre muy corto' : undefined,
        }}
      >
        {(field) => (
          <div className="form-field">
            <label htmlFor="full_name">Nombre completo</label>
            <input
              id="full_name"
              type="text"
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
              placeholder="Juan Pérez"
            />
            {field.state.meta.isTouched && field.state.meta.errors.length > 0 && (
              <span className="field-error">{field.state.meta.errors.join(', ')}</span>
            )}
          </div>
        )}
      </Field>

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
          onChange: ({ value }) =>
            !value
              ? 'Contraseña es requerida'
              : value.length < 8
                ? 'La contraseña debe tener al menos 8 caracteres'
                : undefined,
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

      <Field
        name="passwordConfirm"
        validators={{
          onChange: ({ value }) => (!value ? 'Confirmar contraseña es requerido' : undefined),
        }}
      >
        {(field) => (
          <div className="form-field">
            <label htmlFor="passwordConfirm">Confirmar contraseña</label>
            <input
              id="passwordConfirm"
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
        {isLoading ? 'Creando cuenta...' : 'Crear Cuenta'}
      </button>

      <p className="form-footer">
        ¿Ya tienes cuenta? <a href="/login">Inicia sesión</a>
      </p>
    </form>
  );
}

export default RegisterForm;
