import { forwardRef } from 'react';
import type { InputHTMLAttributes } from 'react';

interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'className'> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="flex flex-col gap-1">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={[
            'w-full rounded-lg border px-3 py-2 text-sm transition-colors',
            'placeholder:text-gray-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-300',
            'dark:bg-gray-800 dark:text-gray-100 dark:placeholder:text-gray-400',
            error
              ? 'border-red-500 focus-visible:border-red-500 focus-visible:ring-red-200 dark:border-red-500'
              : 'border-gray-300 focus-visible:border-primary dark:border-gray-600',
          ].join(' ')}
          {...props}
        />
        {error && <span className="text-xs text-red-600 dark:text-red-400">{error}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
