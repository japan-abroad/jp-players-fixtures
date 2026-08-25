import KickoffBoard from "@/components/KickoffBoard";
import MatchCard from "@/components/MatchCard";
import AffiliateSlot from "@/components/AffiliateSlot";
import { getAllMatchesSorted } from "@/lib/data";
import { toJstDateKey, toJstDateLabel } from "@/lib/time";

export default function HomePage() {
  const matches = getAllMatchesSorted();
  const upcoming = matches.filter((m) => new Date(m.kickoff_utc).getTime() >= Date.now());
  const boardMatches = upcoming.slice(0, 8);

  const groups = new Map<string, typeof upcoming>();
  for (const m of upcoming) {
    const key = toJstDateKey(m.kickoff_utc);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(m);
  }

  return (
    <div>
      <KickoffBoard matches={boardMatches} />

      <section className="mx-auto max-w-5xl px-4 py-8">
        <h1 className="font-display text-2xl font-bold uppercase tracking-tight text-[var(--ink)]">
          直近の試合予定
        </h1>
        <p className="mt-1 text-sm text-[var(--ink-soft)]">
          欧州クラブに所属する日本人選手の試合を、日本時間(JST)で表示しています。
        </p>

        <div className="mt-6 flex flex-col gap-8">
          {[...groups.entries()].map(([dateKey, dayMatches]) => (
            <div key={dateKey}>
              <h2 className="border-b border-[var(--line)] pb-2 font-display text-lg font-semibold text-[var(--samurai)]">
                {toJstDateLabel(dayMatches[0].kickoff_utc)}
              </h2>
              <div className="mt-3 flex flex-col gap-3">
                {dayMatches.map((m) => (
                  <MatchCard key={m.fixture_id} match={m} />
                ))}
              </div>
            </div>
          ))}
          {groups.size === 0 && (
            <p className="text-sm text-[var(--ink-soft)]">
              現在表示できる試合がありません。データを更新中です。
            </p>
          )}
        </div>
        <AffiliateSlot context="home" />
      </section>
    </div>
  );
}
