/**
 * Login Page
 * Following FSD: pages/ directory
 */
import { LoginForm } from '../features/auth/LoginForm';

export function LoginPage() {
  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>🍔 Food Store</h1>
          <p>Inicia sesión para continuar</p>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}

export default LoginPage;