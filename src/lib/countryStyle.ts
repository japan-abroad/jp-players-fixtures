export const COUNTRY_COLOR: Record<string, string> = {
  eng: "#1d4ed8",
  esp: "#dc2626",
  ger: "#374151",
  ita: "#059669",
  fra: "#2563eb",
  ned: "#ea580c",
  por: "#065f46",
  bel: "#d97706",
  sco: "#7c3aed",
  tur: "#b91c1c",
};

export function countryColor(code: string): string {
  return COUNTRY_COLOR[code] ?? "#4a5160";
}
