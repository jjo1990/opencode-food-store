interface Props {
  estado: string;
  className?: string;
}

const BADGE_STYLES: Record<string, string> = {
  PENDIENTE: 'bg-amber-100 text-amber-800',
  CONFIRMADO: 'bg-blue-100 text-blue-800',
  EN_PREPARACION: 'bg-indigo-100 text-indigo-800',
  EN_CAMINO: 'bg-purple-100 text-purple-800',
  ENTREGADO: 'bg-green-100 text-green-800',
  CANCELADO: 'bg-red-100 text-red-800',
};

const ESTADO_LABELS: Record<string, string> = {
  PENDIENTE: 'Pendiente',
  CONFIRMADO: 'Confirmado',
  EN_PREPARACION: 'En Preparación',
  EN_CAMINO: 'En Camino',
  ENTREGADO: 'Entregado',
  CANCELADO: 'Cancelado',
};

export function OrderBadge({ estado, className = '' }: Props) {
  const style = BADGE_STYLES[estado] || 'bg-gray-100 text-gray-800';
  const label = ESTADO_LABELS[estado] || estado;

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${style} ${className}`}
    >
      {label}
    </span>
  );
}

export default OrderBadge;
