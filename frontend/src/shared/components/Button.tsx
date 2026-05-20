import type { ButtonHTMLAttributes, AnchorHTMLAttributes, ReactNode } from 'react';

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';

interface ButtonBaseProps {
  variant?: Variant;
  isLoading?: boolean;
  children: ReactNode;
  className?: string;
}

type ButtonAsButton = ButtonBaseProps &
  Omit<ButtonHTMLAttributes<HTMLButtonElement>, keyof ButtonBaseProps> & {
    as?: 'button';
  };

type ButtonAsLink = ButtonBaseProps &
  Omit<AnchorHTMLAttributes<HTMLAnchorElement>, keyof ButtonBaseProps> & {
    as: 'a';
    href: string;
  };

type ButtonProps = ButtonAsButton | ButtonAsLink;

const variantStyles: Record<Variant, string> = {
  primary: 'bg-primary text-white hover:bg-primary-600 focus:ring-primary-300',
  secondary: 'border-2 border-primary text-primary hover:bg-primary-50 focus:ring-primary-200',
  ghost: 'text-gray-600 hover:bg-gray-100 focus:ring-gray-200',
  danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-300',
};

export function Button(props: ButtonProps) {
  const { variant = 'primary', isLoading = false, className = '', children } = props;

  const baseClasses =
    'inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  const variantClasses = variantStyles[variant];
  const classes = [baseClasses, variantClasses, className].join(' ');

  if (props.as === 'a') {
    const { as: _as, variant: _var, isLoading: _load, ...anchorProps } = props as ButtonAsLink;
    void _as;
    void _var;
    void _load;
    return (
      <a className={classes} {...anchorProps}>
        {isLoading && <SpinnerInline />}
        {children}
      </a>
    );
  }

  const { as: _as2, variant: _var2, isLoading: _load2, ...buttonProps } = props as ButtonAsButton;
  void _as2;
  void _var2;
  void _load2;
  return (
    <button className={classes} disabled={isLoading || buttonProps.disabled} {...buttonProps}>
      {isLoading && <SpinnerInline />}
      {children}
    </button>
  );
}

function SpinnerInline() {
  return (
    <svg
      className="h-4 w-4 animate-spin"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  );
}

export default Button;
