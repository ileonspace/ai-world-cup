export const chartPalette = [
  '#0f766e',
  '#2563eb',
  '#d97706',
  '#7c3aed',
  '#dc2626',
  '#059669',
  '#be185d',
  '#4f46e5',
  '#ca8a04',
  '#0891b2',
  '#9333ea',
  '#ea580c'
];

export function colorForIndex(index: number): string {
  return chartPalette[index % chartPalette.length];
}
