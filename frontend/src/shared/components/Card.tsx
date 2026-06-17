import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  hoverable?: boolean;
  className?: string;
}

export function Card({ children, hoverable = false, className = '' }: CardProps) {
  const classes = [
    'rounded-xl bg-white shadow-md p-6 dark:bg-gray-800 dark:border dark:border-gray-700 dark:shadow-gray-900/30',
    hoverable ? 'transition-shadow hover:shadow-lg dark:hover:shadow-gray-900/50' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return <div className={classes}>{children}</div>;
}

export default Card;
