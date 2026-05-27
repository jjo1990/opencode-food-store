export interface OrderItem {
  id: string;
  producto_id: string;
  nombre_snapshot: string;
  precio_snapshot: number;
  cantidad: number;
  subtotal: number;
  personalizacion: string[] | null;
}

export interface OrderHistoryItem {
  estado_desde: string | null;
  estado_nuevo: string;
  actor_id: string | null;
  motivo: string | null;
  created_at: string;
}

export interface Order {
  id: string;
  estado_codigo: string;
  subtotal: number;
  costo_envio: number;
  total: number;
  created_at: string;
}

export interface OrderDetail extends Order {
  items: OrderItem[];
  historial: OrderHistoryItem[];
}
