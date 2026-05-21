export interface Address {
  id: string;
  usuario_id: string;
  alias: string | null;
  calle: string;
  numero: string;
  piso: string | null;
  departamento: string | null;
  ciudad: string;
  codigo_postal: string;
  referencia: string | null;
  es_principal: boolean;
  created_at: string;
  updated_at: string;
}
