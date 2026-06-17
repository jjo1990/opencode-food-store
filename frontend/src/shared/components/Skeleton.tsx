import { useState, useEffect } from 'react';

type SkeletonVariant = 'text' | 'circle' | 'card';

interface SkeletonProps {
  variant?: SkeletonVariant;
  width?: string;
  height?: string;
  className?: string;
  count?: number;
  delay?: number;
}

function SkeletonItem({ variant = 'text', width, height, className = '' }: SkeletonProps) {
  const baseClasses = 'animate-pulse bg-gray-200 rounded dark:bg-gray-700';

  const variantClasses: Record<SkeletonVariant, string> = {
    text: 'h-4 w-full rounded',
    circle: 'rounded-full',
    card: 'h-48 w-full rounded-xl',
  };

  const style: Record<string, string> = {};
  if (width) style.width = width;
  if (height) style.height = height;

  return (
    <div
      className={[baseClasses, variantClasses[variant], className].join(' ')}
      style={Object.keys(style).length ? style : undefined}
    />
  );
}

export function Skeleton({ delay = 0, count = 1, ...props }: SkeletonProps) {
  const [visible, setVisible] = useState(delay <= 0);

  useEffect(() => {
    if (delay <= 0) return;
    const timer = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  if (!visible) return null;

  if (count <= 1) return <SkeletonItem {...props} />;

  return (
    <div className="space-y-2">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonItem key={i} {...props} />
      ))}
    </div>
  );
}

export default Skeleton;
