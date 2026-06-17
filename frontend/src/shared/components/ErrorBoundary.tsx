import { Component, ReactNode } from 'react';
import { devLogger } from '../utils/logger';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    devLogger.error('ErrorBoundary caught error', {
      error: error.message,
      componentStack: errorInfo.componentStack,
    });
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <main className="flex min-h-screen items-center justify-center bg-gray-50 px-4 dark:bg-gray-950">
          <div className="w-full max-w-md rounded-xl bg-white p-8 text-center shadow-lg dark:bg-gray-800 dark:shadow-gray-900/30">
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-gray-100">
              😵 Algo salio mal
            </h2>
            <p className="mb-6 text-gray-600 dark:text-gray-300">
              Ha ocurrido un error inesperado.
            </p>
            {this.state.error && (
              <pre className="mb-6 overflow-x-auto rounded-lg bg-gray-100 p-4 text-left text-sm text-red-600 dark:bg-gray-700 dark:text-red-400">
                {this.state.error.message}
              </pre>
            )}
            <button
              onClick={() => window.location.reload()}
              className="rounded-lg bg-primary px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-primary-600"
            >
              Recargar pagina
            </button>
          </div>
        </main>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
