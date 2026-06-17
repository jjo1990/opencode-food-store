interface TimelineEntry {
  created_at: string;
  estado_nuevo: string;
  actor_id: string | null;
  motivo: string | null;
}

interface Props {
  history: TimelineEntry[];
  currentState?: string;
  className?: string;
}

const ESTADO_COLORS: Record<string, string> = {
  PENDIENTE: 'bg-amber-500',
  CONFIRMADO: 'bg-blue-500',
  EN_PREPARACION: 'bg-indigo-500',
  EN_CAMINO: 'bg-purple-500',
  ENTREGADO: 'bg-green-500',
  CANCELADO: 'bg-red-500',
};

const ESTADO_LABELS: Record<string, string> = {
  PENDIENTE: 'Pendiente',
  CONFIRMADO: 'Confirmado',
  EN_PREPARACION: 'En Preparacion',
  EN_CAMINO: 'En Camino',
  ENTREGADO: 'Entregado',
  CANCELADO: 'Cancelado',
};

const FSM_ORDER = ['PENDIENTE', 'CONFIRMADO', 'EN_PREPARACION', 'EN_CAMINO', 'ENTREGADO'];

function CheckIcon() {
  return (
    <svg
      className="h-4 w-4 text-white"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2.5}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  );
}

function CancelIcon() {
  return (
    <svg
      className="h-4 w-4 text-white"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2.5}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

function DotIcon() {
  return <div className="h-2.5 w-2.5 rounded-full bg-white" />;
}

export function OrderTimeline({ history, currentState, className = '' }: Props) {
  const historyMap = new Map<string, TimelineEntry>();
  for (const h of history) {
    historyMap.set(h.estado_nuevo, h);
  }

  interface Step {
    estado: string;
    entry: TimelineEntry | undefined;
    isFuture: boolean;
    isCurrent: boolean;
  }

  let steps: Step[];

  if (!currentState || currentState === 'CANCELADO') {
    steps = history.map((h) => ({
      estado: h.estado_nuevo,
      entry: h,
      isFuture: false,
      isCurrent: h.estado_nuevo === currentState,
    }));
  } else {
    const currentIdx = FSM_ORDER.indexOf(currentState);
    if (currentIdx === -1) {
      steps = history.map((h) => ({
        estado: h.estado_nuevo,
        entry: h,
        isFuture: false,
        isCurrent: false,
      }));
    } else {
      steps = FSM_ORDER.slice(0, currentIdx + 1).map((estado) => ({
        estado,
        entry: historyMap.get(estado),
        isFuture: !historyMap.has(estado),
        isCurrent: estado === currentState,
      }));
    }
  }

  return (
    <div className={`space-y-0 ${className}`}>
      {steps.map((step, idx) => {
        const isLast = idx === steps.length - 1;
        const colorClass = step.isFuture
          ? 'bg-gray-300 dark:bg-gray-600'
          : ESTADO_COLORS[step.estado] || 'bg-gray-500';
        const textClass = step.isFuture ? 'text-gray-500 dark:text-gray-400' : 'text-gray-900 dark:text-gray-100';
        const subTextClass = step.isFuture ? 'text-gray-400 dark:text-gray-500' : 'text-gray-500 dark:text-gray-400';

        return (
          <div key={idx} className="relative flex gap-4 pb-8 last:pb-0">
            <div className="flex flex-col items-center">
              <div
                className={`relative z-10 flex h-8 w-8 items-center justify-center rounded-full ${colorClass} ${
                  step.isCurrent && !step.isFuture
                    ? 'ring-2 ring-gray-300 ring-offset-2 ring-offset-white dark:ring-gray-500 dark:ring-offset-gray-900'
                    : ''
                }`}
              >
                {step.isFuture ? (
                  <DotIcon />
                ) : step.estado === 'CANCELADO' ? (
                  <CancelIcon />
                ) : (
                  <CheckIcon />
                )}
              </div>
              {!isLast && <div className="mt-1 w-0.5 flex-1 bg-gray-200 dark:bg-gray-700" />}
            </div>
            <div className="flex-1 pb-2">
              <p className={`font-medium ${textClass}`}>
                {ESTADO_LABELS[step.estado] || step.estado}
                {step.isCurrent && !step.isFuture && (
                  <span className="ml-2 inline-flex items-center rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                    Actual
                  </span>
                )}
              </p>
              {step.entry?.created_at && (
                <p className={`text-sm ${subTextClass}`}>
                  {new Date(step.entry.created_at).toLocaleString()}
                </p>
              )}
              {step.entry?.actor_id && (
                <p className={`text-sm ${step.isFuture ? 'text-gray-400 dark:text-gray-500' : 'text-gray-500 dark:text-gray-400'}`}>
                  por {step.entry.actor_id}
                </p>
              )}
              {step.entry?.motivo && (
                <p
                  className={`text-sm italic ${step.isFuture ? 'text-gray-400 dark:text-gray-500' : 'text-gray-500 dark:text-gray-400'}`}
                >
                  &ldquo;{step.entry.motivo}&rdquo;
                </p>
              )}
              {step.isFuture && <p className="text-sm text-gray-400 dark:text-gray-500">Pendiente</p>}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default OrderTimeline;
