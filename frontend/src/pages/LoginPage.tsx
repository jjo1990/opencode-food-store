import { LoginForm } from '../features/auth/LoginForm';

export function LoginPage() {
  return (
    <main className="flex min-h-[80vh] items-center justify-center px-4 py-12">
      <section
        aria-labelledby="login-heading"
        className="w-full max-w-md rounded-xl bg-white p-8 shadow-md dark:bg-gray-800 dark:shadow-gray-900/30"
      >
        <div className="mb-6 text-center">
          <h1 id="login-heading" className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            🍔 Food Store
          </h1>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">Inicia sesion para continuar</p>
        </div>
        <LoginForm />
      </section>
    </main>
  );
}

export default LoginPage;
