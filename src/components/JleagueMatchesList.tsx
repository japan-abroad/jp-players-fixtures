"use client";

import { useMemo, useState } from "react";
import type { Match } from "@/lib/data";
import { toJstDateLabel } from "@/lib/time";
import { groupMatchesByDate } from "@/lib/matches";
import { translateTeamName } from "@/lib/teamNames";
import MatchRow from "./MatchRow";

const COMPETITIONS = ["J1リーグ", "J2リーグ", "J3リーグ", "ルヴァンカップ", "天皇杯"];

export default function JleagueMatchesList({ matches }: { matches: Match[] }) {
  const [showPast, setShowPast] = useState(false);
  const [activeLeagues, setActiveLeagues] = useState<Set<string>>(new Set());
  const [query, setQuery] = useState("");

  const toggleLeague = (name: string) => {
    setActiveLeagues((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return matches.filter((m) => {
      const okLeague = activeLeagues.size === 0 || activeLeagues.has(m.league_name);
      const okQuery =
        !q ||
        translateTeamName(m.home_team).toLowerCase().includes(q) ||
        translateTeamName(m.away_team).toLowerCase().includes(q);
      return okLeague && okQuery;
    });
  }, [matches, activeLeagues, query]);

  const groups = useMemo(() => groupMatchesByDate(filtered, showPast), [filtered, showPast]);

  return (
    <div>
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex overflow-hidden rounded-full border border-[var(--line)]">
          <button
            className={`px-4 py-3 sm:py-1.5 text-xs font-bold ${
              !showPast ? "bg-[var(--samurai)] text-white" : "bg-white text-[var(--ink-soft)]"
            }`}
            onClick={() => setShowPast(false)}
          >
            今後の試合
          </button>
          <button
            className={`px-4 py-3 sm:py-1.5 text-xs font-bold ${
              showPast ? "bg-[var(--samurai)] text-white" : "bg-white text-[var(--ink-soft)]"
            }`}
            onClick={() => setShowPast(true)}
          >
            過去の試合結果
          </button>
        </div>

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="チーム名で絞り込み"
          className="w-full max-w-xs rounded-full border border-[var(--line)] bg-[var(--paper-raised)] px-4 py-1.5 text-sm text-[var(--ink)] placeholder:text-[var(--ink-soft)] focus:border-[var(--samurai)] focus:outline-none"
        />
      </div>

      <div className="country-filter-scroll mt-3 flex items-center gap-2 overflow-x-auto pb-1">
        {COMPETITIONS.map((name) => (
          <button
            key={name}
            className={`chip-btn${activeLeagues.has(name) ? " active" : ""}`}
            style={
              activeLeagues.has(name)
                ? { backgroundColor: "var(--samurai)", borderColor: "transparent" }
                : undefined
            }
            onClick={() => toggleLeague(name)}
          >
            {name}
          </button>
        ))}
        {activeLeagues.size > 0 && (
          <button className="chip-btn" onClick={() => setActiveLeagues(new Set())}>
            絞り込み解除
          </button>
        )}
      </div>

      <div className="mt-6">
        {groups.map(([dateKey, dayMatches]) => (
          <div key={dateKey}>
            <h2 className="date-heading">{toJstDateLabel(dayMatches[0].kickoff_utc)}</h2>
            {dayMatches.map((m) => (
              <MatchRow key={m.fixture_id} match={m} />
            ))}
          </div>
        ))}
        {groups.length === 0 && (
          <p className="mt-6 text-sm text-[var(--ink-soft)]">
            条件に合う試合がありません。絞り込みを解除してみてください。
          </p>
        )}
      </div>
    </div>
  );
}
