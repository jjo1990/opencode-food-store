import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <main className="flex min-h-[60vh] flex-col items-center justify-center gap-6 px-4 text-center">
      <div className="text-8xl font-bold text-gray-200 dark:text-gray-700">404</div>
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Pagina no encontrada</h1>
        <p className="mt-2 text-gray-500 dark:text-gray-400">La pagina que estas buscando no existe o fue movida.</p>
      </div>
      <Link
        to="/catalog"
        className="rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-primary-600"
      >
        Volver al inicio
      </Link>
    </main>
  );
}

export default NotFoundPage;
