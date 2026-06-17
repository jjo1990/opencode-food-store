interface ErrorDisplayProps {
  message: string;
  title?: string;
  onRetry?: () => void;
}

export function ErrorDisplay({ message, title = 'Algo salio mal', onRetry }: ErrorDisplayProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 rounded-xl bg-red-50 p-8 text-center dark:bg-red-900/20 dark:border dark:border-red-800">
      <svg className="h-12 w-12 text-red-400 dark:text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
      <div>
        <h3 className="text-lg font-semibold text-red-800 dark:text-red-300">{title}</h3>
        <p className="mt-1 text-sm text-red-600 dark:text-red-400">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-red-700"
        >
          Reintentar
        </button>
      )}
    </div>
  );
}

export default ErrorDisplay;
