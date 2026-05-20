import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-6 px-4 text-center">
      <div className="text-8xl font-bold text-gray-200">404</div>
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Página no encontrada</h1>
        <p className="mt-2 text-gray-500">La página que estás buscando no existe o fue movida.</p>
      </div>
      <Link
        to="/catalog"
        className="rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-primary-600"
      >
        Volver al inicio
      </Link>
    </div>
  );
}

export default NotFoundPage;
