"use client";

import { useMemo, useState } from "react";
import Link from "next/link";

export type PlayerListItem = {
  slug: string;
  name: string;
  teamName: string;
};

export default function PlayersFilterList({
  groups,
}: {
  groups: [string, PlayerListItem[]][];
}) {
  const [query, setQuery] = useState("");

  const filteredGroups = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return groups;
    return groups
      .map(([league, players]) => [
        league,
        players.filter(
          (p) => p.name.toLowerCase().includes(q) || p.teamName.toLowerCase().includes(q)
        ),
      ] as [string, PlayerListItem[]])
      .filter(([, players]) => players.length > 0);
  }, [groups, query]);

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="選手名・チーム名で絞り込み"
        className="mt-4 w-full max-w-sm rounded-full border border-[var(--line)] bg-[var(--paper-raised)] px-4 py-2 text-sm text-[var(--ink)] placeholder:text-[var(--ink-soft)] focus:border-[var(--samurai)] focus:outline-none"
      />

      {filteredGroups.map(([leagueName, players]) => (
        <div key={leagueName} className="mt-8 first:mt-6">
          <h2 className="font-display text-sm font-bold uppercase tracking-tight text-[var(--samurai)]">
            {leagueName}
          </h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {players.map((p) => (
              <Link
                key={p.slug}
                href={`/players/${p.slug}/`}
                className="inline-block rounded-full bg-[var(--samurai)]/10 px-4 py-1.5 text-sm font-semibold text-[var(--samurai)] shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:bg-[var(--samurai)]/20 hover:shadow-md"
              >
                {p.name}
                <span className="ml-1 text-xs font-normal text-[var(--ink-soft)]">
                  {p.teamName}
                </span>
              </Link>
            ))}
          </div>
        </div>
      ))}
      {filteredGroups.length === 0 && (
        <p className="mt-6 text-sm text-[var(--ink-soft)]">
          「{query}」に一致する選手が見つかりませんでした。
        </p>
      )}
    </div>
  );
}
