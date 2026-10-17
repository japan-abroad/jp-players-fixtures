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

/** 試合日の切り替え時刻(JST)。これより前の深夜キックオフは前日の試合として扱う。 */
const MATCH_DAY_CUTOFF_HOUR = 6;

function shiftToMatchDay(isoUtc: string): string {
  return new Date(new Date(isoUtc).getTime() - MATCH_DAY_CUTOFF_HOUR * 3600 * 1000).toISOString();
}

export function toMatchDayKey(isoUtc: string): string {
  // JST 0:00〜5:59開始の試合は前日の日付キーにまとめる。
  return toJstDateKey(shiftToMatchDay(isoUtc));
}

export function toMatchDayLabel(isoUtc: string): string {
  return toJstDateLabel(shiftToMatchDay(isoUtc));
}

export function toMatchDayTime(isoUtc: string): string {
  // 前日扱いの深夜キックオフは "24:30" "27:00" のように24時以降表記にする。
  const [h, m] = toJstTime(isoUtc).split(":").map(Number);
  const hour = h < MATCH_DAY_CUTOFF_HOUR ? h + 24 : h;
  return `${String(hour).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
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
