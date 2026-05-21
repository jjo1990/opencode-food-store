export interface UserProfile {
  id: string;
  email: string;
  full_name: string | null;
  telefono: string | null;
  roles: string[];
  created_at: string;
}
