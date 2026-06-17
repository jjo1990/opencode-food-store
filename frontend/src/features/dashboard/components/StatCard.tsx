import Card from '../../../shared/components/Card';
import Skeleton from '../../../shared/components/Skeleton';
import ErrorDisplay from '../../../shared/components/ErrorDisplay';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: string;
  trend?: { value: number; isPositive: boolean };
  isLoading?: boolean;
  error?: string;
  className?: string;
}

export function StatCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  isLoading,
  error,
  className = '',
}: StatCardProps) {
  if (error) {
    return (
      <Card className={className}>
        <ErrorDisplay message={error} />
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card className={className}>
        <div className="flex items-center gap-3">
          <Skeleton variant="circle" width="40px" height="40px" />
          <div className="flex-1 space-y-2">
            <Skeleton variant="text" width="60%" />
            <Skeleton variant="text" width="80%" height="24px" />
          </div>
        </div>
      </Card>
    );
  }

  const formattedValue =
    typeof value === 'number'
      ? value % 1 !== 0
        ? `$${value.toFixed(2)}`
        : value.toLocaleString('es-AR')
      : value;

  return (
    <Card hoverable className={className}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
          <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-gray-100">{formattedValue}</p>
          {subtitle && <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{subtitle}</p>}
          {trend && (
            <p
              className={`mt-1 text-xs font-medium ${
                trend.isPositive ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {trend.isPositive ? '▲' : '▼'} {trend.value}%
            </p>
          )}
        </div>
        {icon && <span className="text-2xl">{icon}</span>}
      </div>
    </Card>
  );
}

export default StatCard;
