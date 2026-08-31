import type { Match } from "./data";
import { toJstDateKey } from "./time";

/** 今後の試合(未来)/過去の試合結果を振り分けて日付ごとにグルーピングする。
 *  過去は新しい日付順、今後は近い日付順に並べる。
 */
export function groupMatchesByDate(matches: Match[], showPast: boolean): [string, Match[]][] {
  const now = Date.now();
  const scoped = matches.filter((m) =>
    showPast ? new Date(m.kickoff_utc).getTime() < now : new Date(m.kickoff_utc).getTime() >= now
  );

  const map = new Map<string, Match[]>();
  for (const m of scoped) {
    const key = toJstDateKey(m.kickoff_utc);
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(m);
  }

  const entries = [...map.entries()];
  entries.sort(([a], [b]) => (showPast ? (a < b ? 1 : -1) : a < b ? -1 : 1));
  return entries;
}
