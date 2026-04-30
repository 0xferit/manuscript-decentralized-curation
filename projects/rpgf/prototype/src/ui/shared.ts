export function fmtToken(value: number | null | undefined, digits = 4): string {
  if (value === null || value === undefined) return "—";
  return value.toFixed(digits);
}

export function fmtPct(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined) return "—";
  return `${(value * 100).toFixed(digits)}%`;
}

export function fmtNum(value: number | null | undefined, digits = 3): string {
  if (value === null || value === undefined) return "—";
  return value.toFixed(digits);
}
