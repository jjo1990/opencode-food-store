import { Skeleton } from './Skeleton';

interface SkeletonTableProps {
  rows?: number;
  columns?: number;
  className?: string;
}

export function SkeletonTable({ rows = 5, columns = 4, className = '' }: SkeletonTableProps) {
  return (
    <div className={`overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700 ${className}`}>
      <div className="min-w-full">
        <div className="bg-gray-50 px-4 py-3 flex gap-4 dark:bg-gray-800">
          {Array.from({ length: columns }).map((_, i) => (
            <Skeleton key={`header-${i}`} variant="text" height="20px" />
          ))}
        </div>
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {Array.from({ length: rows }).map((_, rowIdx) => (
            <div
              key={`row-${rowIdx}`}
              className={`px-4 py-3 flex gap-4 ${
                rowIdx % 2 === 0 ? 'bg-white dark:bg-gray-900' : 'bg-gray-50 dark:bg-gray-800'
              }`}
            >
              {Array.from({ length: columns }).map((_, colIdx) => (
                <Skeleton key={`cell-${rowIdx}-${colIdx}`} variant="text" height="16px" />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default SkeletonTable;
