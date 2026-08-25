/** キックオフ時刻(UTC ISO文字列)を日本時間(JST, UTC+9)の各種表示形式に変換するユーティリティ。
 *  ビルド環境のタイムゾーンに依存しないよう、Intlのtimezone指定で明示的にJSTへ変換する。
 */

const JST_TZ = "Asia/Tokyo";

export function toJstDateKey(isoUtc: string): string {
  // "2026-08-26" 形式。日付グルーピングのキーに使う。
  const d = new Date(isoUtc);
  return new Intl.DateTimeFormat("sv-SE", { timeZone: JST_TZ }).format(d); // sv-SEはYYYY-MM-DD形式
}

export function toJstDateLabel(isoUtc: string): string {
  const d = new Date(isoUtc);
  const weekday = new Intl.DateTimeFormat("ja-JP", {
    timeZone: JST_TZ,
    weekday: "short",
  }).format(d);
  const md = new Intl.DateTimeFormat("ja-JP", {
    timeZone: JST_TZ,
    month: "long",
    day: "numeric",
  }).format(d);
  return `${md}(${weekday})`;
}

export function toJstTime(isoUtc: string): string {
  const d = new Date(isoUtc);
  return new Intl.DateTimeFormat("ja-JP", {
    timeZone: JST_TZ,
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(d);
}

export function toLocalKickoffLabel(isoUtc: string): string {
  const d = new Date(isoUtc);
  return new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: "UTC",
  }).format(d);
}
