export interface NavItem {
  label: string;
  path: string;
  icon: string;
  allowedRoles?: string[];
  section: 'main' | 'admin' | 'stock' | 'pedidos';
}

const menuItems: NavItem[] = [
  { label: 'Catálogo', path: '/catalog', icon: '🏪', section: 'main' },
  { label: 'Mi Carrito', path: '/cart', icon: '🛒', allowedRoles: ['CLIENT'], section: 'main' },
  { label: 'Mis Pedidos', path: '/orders', icon: '📦', allowedRoles: ['CLIENT'], section: 'main' },
  { label: 'Perfil', path: '/profile', icon: '👤', allowedRoles: ['CLIENT'], section: 'main' },
  {
    label: 'Direcciones',
    path: '/addresses',
    icon: '📍',
    allowedRoles: ['CLIENT'],
    section: 'main',
  },
  { label: 'Dashboard', path: '/admin', icon: '📊', allowedRoles: ['ADMIN'], section: 'admin' },
  {
    label: 'Usuarios',
    path: '/admin/users',
    icon: '👥',
    allowedRoles: ['ADMIN'],
    section: 'admin',
  },
  {
    label: 'Productos',
    path: '/admin/products',
    icon: '🏪',
    allowedRoles: ['ADMIN', 'STOCK'],
    section: 'admin',
  },
  { label: 'Stock', path: '/admin/stock', icon: '📦', allowedRoles: ['ADMIN'], section: 'admin' },
  {
    label: 'Pedidos',
    path: '/admin/orders',
    icon: '📋',
    allowedRoles: ['ADMIN', 'PEDIDOS'],
    section: 'admin',
  },
  {
    label: 'Reportes',
    path: '/admin/reports',
    icon: '📈',
    allowedRoles: ['ADMIN'],
    section: 'admin',
  },
  {
    label: 'Productos',
    path: '/stock/products',
    icon: '🏪',
    allowedRoles: ['STOCK'],
    section: 'stock',
  },
  {
    label: 'Categorías',
    path: '/stock/categories',
    icon: '🏷️',
    allowedRoles: ['STOCK'],
    section: 'stock',
  },
  {
    label: 'Gestionar Stock',
    path: '/stock/manage',
    icon: '📦',
    allowedRoles: ['STOCK'],
    section: 'stock',
  },
  {
    label: 'Panel de Pedidos',
    path: '/pedidos',
    icon: '📋',
    allowedRoles: ['PEDIDOS'],
    section: 'pedidos',
  },
  {
    label: 'Reportes',
    path: '/pedidos/reports',
    icon: '📈',
    allowedRoles: ['PEDIDOS'],
    section: 'pedidos',
  },
];

const sectionLabels: Record<string, string> = {
  main: 'General',
  admin: 'Administración',
  stock: 'Stock',
  pedidos: 'Pedidos',
};

export function getMenuItemsByRole(roles: string[] = []): NavItem[] {
  return menuItems.filter(
    (item) => !item.allowedRoles || item.allowedRoles.some((r) => roles.includes(r))
  );
}

export function getMenuItemsBySection(roles: string[] = []): Record<string, NavItem[]> {
  const items = getMenuItemsByRole(roles);
  const grouped: Record<string, NavItem[]> = {};
  for (const item of items) {
    if (!grouped[item.section]) grouped[item.section] = [];
    grouped[item.section].push(item);
  }
  return grouped;
}

export function getSectionLabel(section: string): string {
  return sectionLabels[section] || section;
}
