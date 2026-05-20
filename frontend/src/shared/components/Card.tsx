import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  hoverable?: boolean;
  className?: string;
}

export function Card({ children, hoverable = false, className = '' }: CardProps) {
  const classes = [
    'rounded-xl bg-white shadow-md p-6',
    hoverable ? 'transition-shadow hover:shadow-lg' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return <div className={classes}>{children}</div>;
}

export default Card;
