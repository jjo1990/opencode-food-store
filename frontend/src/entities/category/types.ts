export interface Category {
  id: string;
  nombre: string;
  slug: string;
  children: Category[];
}
