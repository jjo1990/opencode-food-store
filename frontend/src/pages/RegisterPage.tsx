/**
 * Register Page
 * Following FSD: pages/ directory
 */
import { RegisterForm } from '../features/auth/RegisterForm';

export function RegisterPage() {
  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>🍔 Food Store</h1>
          <p>Crea tu cuenta para comenzar</p>
        </div>
        <RegisterForm />
      </div>
    </div>
  );
}

export default RegisterPage;