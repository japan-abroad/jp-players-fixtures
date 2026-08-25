import type { MatchWithClub } from "@/lib/data";
import { toJstDateLabel, toJstTime } from "@/lib/time";

export default function KickoffBoard({ matches }: { matches: MatchWithClub[] }) {
  if (matches.length === 0) {
    return (
      <section className="flap px-4 py-10 text-center text-white">
        <p className="font-display text-lg uppercase tracking-wide">Next Kickoff</p>
        <p className="mt-2 text-sm text-white/80">
          現在表示できる試合がありません。データを更新中です。
        </p>
      </section>
    );
  }

  return (
    <section className="flap">
      <div className="mx-auto max-w-5xl px-4 py-6">
        <p className="font-display text-sm uppercase tracking-[0.2em] text-white/70">
          Next Kickoff · 日本時間
        </p>
        <div className="mt-3 flex gap-3 overflow-x-auto pb-2">
          {matches.map((m, i) => (
            <a
              key={m.fixture_id}
              href={`#match-${m.fixture_id}`}
              className="flap-animate flex min-w-[168px] shrink-0 flex-col gap-2 rounded-sm border border-white/15 bg-black/20 px-4 py-3 transition hover:bg-black/30"
              style={{ animationDelay: `${i * 60}ms` }}
            >
              <span className="flap-digit font-mono text-3xl font-bold text-white">
                {toJstTime(m.kickoff_utc)}
              </span>
              <span className="text-xs text-white/70">{toJstDateLabel(m.kickoff_utc)}</span>
              <span className="text-sm font-semibold text-white">
                {m.home_team} vs {m.away_team}
              </span>
              <span className="truncate text-xs text-[#8fd6ac]">
                {m.club.players.map((p) => p.name).join("・")}
              </span>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
