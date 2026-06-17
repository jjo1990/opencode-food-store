import { Skeleton } from './Skeleton';

interface SkeletonCardProps {
  className?: string;
}

export function SkeletonCard({ className = '' }: SkeletonCardProps) {
  return (
    <div className={`rounded-xl border border-gray-200 shadow-md overflow-hidden dark:border-gray-700 dark:shadow-gray-900/30 ${className}`}>
      <Skeleton variant="card" />
      <div className="p-4 space-y-3">
        <Skeleton variant="text" width="75%" height="20px" />
        <Skeleton variant="text" width="50%" height="16px" />
        <Skeleton variant="text" width="33%" height="16px" />
        <Skeleton variant="text" width="96px" height="40px" />
      </div>
    </div>
  );
}

export default SkeletonCard;
