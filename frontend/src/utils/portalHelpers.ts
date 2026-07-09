const APP_ICON_GRADIENTS = [
  'linear-gradient(135deg, #E91E8C 0%, #FF1493 100%)',
  'linear-gradient(135deg, #DB2777 0%, #F472B6 100%)',
  'linear-gradient(135deg, #BE185D 0%, #E91E8C 100%)',
  'linear-gradient(135deg, #9D174D 0%, #DB2777 100%)',
];

export const ROLE_LABELS: Record<string, string> = {
  admin: 'Administrador global',
  area_admin: 'Administrador de área',
  usuario: 'Colaborador',
};

export function getRoleLabel(role: string): string {
  return ROLE_LABELS[role] ?? role;
}

export function getAppInitial(name: string): string {
  const trimmed = name.trim();
  if (!trimmed) return 'A';
  return trimmed.charAt(0).toUpperCase();
}

export function getAppGradient(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i += 1) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % APP_ICON_GRADIENTS.length;
  return APP_ICON_GRADIENTS[index];
}

export function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Buenos días';
  if (hour < 18) return 'Buenas tardes';
  return 'Buenas noches';
}

export function normalizeUrlKey(url: string): string {
  return url.trim().replace(/\/+$/, '').toLowerCase();
}

/** Quita duplicados solo si nombre Y url son iguales. */
export function dedupeApps<T extends { name: string; url: string }>(items: T[]): T[] {
  const seen = new Set<string>();
  return items.filter(item => {
    const nameKey = item.name.trim().toLowerCase();
    const urlKey = normalizeUrlKey(item.url);
    if (!nameKey || !urlKey) {
      return true;
    }
    const key = `${nameKey}|${urlKey}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}
