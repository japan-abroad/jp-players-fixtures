"use client";

import { useMemo, useState } from "react";
import type { Match } from "@/lib/data";
import { toJstDateKey, toJstDateLabel } from "@/lib/time";
import { countryColor } from "@/lib/countryStyle";
import MatchRow from "./MatchRow";

const COUNTRIES: { code: string; label: string }[] = [
  { code: "eng", label: "イングランド" },
  { code: "esp", label: "スペイン" },
  { code: "ger", label: "ドイツ" },
  { code: "ita", label: "イタリア" },
  { code: "fra", label: "フランス" },
  { code: "ned", label: "オランダ" },
  { code: "por", label: "ポルトガル" },
  { code: "bel", label: "ベルギー" },
  { code: "sco", label: "スコットランド" },
  { code: "tur", label: "トルコ" },
];

export default function MatchesList({ matches }: { matches: Match[] }) {
  const [jpOnly, setJpOnly] = useState(false);
  const [showPast, setShowPast] = useState(false);
  const [activeCountries, setActiveCountries] = useState<Set<string>>(new Set());

  const toggleCountry = (code: string) => {
    setActiveCountries((prev) => {
      const next = new Set(prev);
      if (next.has(code)) next.delete(code);
      else next.add(code);
      return next;
    });
  };

  const scoped = useMemo(() => {
    const now = Date.now();
    return matches.filter((m) =>
      showPast ? new Date(m.kickoff_utc).getTime() < now : new Date(m.kickoff_utc).getTime() >= now
    );
  }, [matches, showPast]);

  const filtered = useMemo(() => {
    return scoped.filter((m) => {
      const okJp = !jpOnly || m.jp_players.length > 0;
      const okCountry = activeCountries.size === 0 || activeCountries.has(m.country_code);
      return okJp && okCountry;
    });
  }, [scoped, jpOnly, activeCountries]);

  const groups = useMemo(() => {
    const map = new Map<string, Match[]>();
    for (const m of filtered) {
      const key = toJstDateKey(m.kickoff_utc);
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(m);
    }
    const entries = [...map.entries()];
    // 過去の試合結果は直近日から新しい順、今後の試合は開催が近い順に並べる
    entries.sort(([a], [b]) => (showPast ? (a < b ? 1 : -1) : a < b ? -1 : 1));
    return entries;
  }, [filtered, showPast]);

  return (
    <div>
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex overflow-hidden rounded-full border border-[var(--line)]">
          <button
            className={`px-4 py-1.5 text-xs font-bold ${
              !showPast ? "bg-[var(--samurai)] text-white" : "bg-white text-[var(--ink-soft)]"
            }`}
            onClick={() => setShowPast(false)}
          >
            今後の試合
          </button>
          <button
            className={`px-4 py-1.5 text-xs font-bold ${
              showPast ? "bg-[var(--samurai)] text-white" : "bg-white text-[var(--ink-soft)]"
            }`}
            onClick={() => setShowPast(true)}
          >
            過去の試合結果
          </button>
        </div>

        <div className="flex overflow-hidden rounded-full border border-[var(--line)]">
          <button
            className={`px-4 py-1.5 text-xs font-bold ${
              !jpOnly ? "bg-[var(--samurai)] text-white" : "bg-white text-[var(--ink-soft)]"
            }`}
            onClick={() => setJpOnly(false)}
          >
            全試合
          </button>
          <button
            className={`px-4 py-1.5 text-xs font-bold ${
              jpOnly ? "bg-[var(--samurai)] text-white" : "bg-white text-[var(--ink-soft)]"
            }`}
            onClick={() => setJpOnly(true)}
          >
            日本人所属クラブのみ
          </button>
        </div>
      </div>

      <div className="country-filter-scroll mt-3 flex items-center gap-2 overflow-x-auto pb-1">
        {COUNTRIES.map((c) => (
          <button
            key={c.code}
            className="chip-btn"
            style={
              activeCountries.has(c.code)
                ? { backgroundColor: countryColor(c.code), borderColor: "transparent" }
                : undefined
            }
            onClick={() => toggleCountry(c.code)}
          >
            {c.label}
          </button>
        ))}
        {activeCountries.size > 0 && (
          <button className="chip-btn" onClick={() => setActiveCountries(new Set())}>
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
