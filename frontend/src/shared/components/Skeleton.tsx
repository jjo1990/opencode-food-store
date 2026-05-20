type SkeletonVariant = 'text' | 'circle' | 'card';

interface SkeletonProps {
  variant?: SkeletonVariant;
  width?: string;
  height?: string;
  className?: string;
}

export function Skeleton({ variant = 'text', width, height, className = '' }: SkeletonProps) {
  const baseClasses = 'animate-pulse bg-gray-200 rounded';

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

export default Skeleton;
