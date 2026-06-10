export function pct(value: number | null | undefined): string {
  return `${((value ?? 0) * 100).toFixed(1)}%`;
}

export function compactDate(value: string | null | undefined): string {
  if (!value) return 'TBD';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}

export function unique<T>(items: T[]): T[] {
  return Array.from(new Set(items));
}
