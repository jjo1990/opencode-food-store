type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  action: string;
  data?: unknown;
}

const isDev = import.meta.env.DEV;

function createLogEntry(level: LogLevel, action: string, data?: unknown): LogEntry {
  return {
    timestamp: new Date().toISOString(),
    level,
    action,
    ...(data !== undefined ? { data } : {}),
  };
}

function log(level: LogLevel, action: string, data?: unknown): void {
  if (!isDev) return;

  const entry = createLogEntry(level, action, data);
  const prefix = '[FoodStore]';

  switch (level) {
    case 'error':
      console.error(prefix, action, entry);
      break;
    case 'warn':
      console.warn(prefix, action, entry);
      break;
    case 'info':
    case 'debug':
    default:
      console.log(prefix, action, entry);
      break;
  }
}

export const devLogger = {
  debug: (action: string, data?: unknown) => log('debug', action, data),
  info: (action: string, data?: unknown) => log('info', action, data),
  warn: (action: string, data?: unknown) => log('warn', action, data),
  error: (action: string, data?: unknown) => log('error', action, data),
};
