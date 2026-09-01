"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import Link from "next/link";

export type ClubListItem = {
  teamId: number;
  name: string;
  logo: string;
  playerNames: string[];
};

export default function ClubsFilterList({
  groups,
}: {
  groups: [string, ClubListItem[]][];
}) {
  const [query, setQuery] = useState("");

  const filteredGroups = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return groups;
    return groups
      .map(([league, clubs]) => [
        league,
        clubs.filter(
          (c) =>
            c.name.toLowerCase().includes(q) ||
            c.playerNames.some((n) => n.toLowerCase().includes(q))
        ),
      ] as [string, ClubListItem[]])
      .filter(([, clubs]) => clubs.length > 0);
  }, [groups, query]);

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="クラブ名・選手名で絞り込み"
        className="mt-4 w-full max-w-sm rounded-full border border-[var(--line)] bg-[var(--paper-raised)] px-4 py-2 text-sm text-[var(--ink)] placeholder:text-[var(--ink-soft)] focus:border-[var(--samurai)] focus:outline-none"
      />

      {filteredGroups.map(([leagueName, clubs]) => (
        <div key={leagueName} className="mt-8 first:mt-6">
          <h2 className="font-display text-sm font-bold uppercase tracking-tight text-[var(--samurai)]">
            {leagueName}
          </h2>
          <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
            {clubs.map((club) => (
              <Link
                key={club.teamId}
                href={`/clubs/${club.teamId}/`}
                className="flex items-center gap-3 rounded-md border border-[var(--line)] bg-[var(--paper-raised)] p-4 shadow-sm transition hover:border-[var(--samurai)]"
              >
                <Image src={club.logo} alt={club.name} width={40} height={40} unoptimized />
                <div>
                  <p className="font-semibold text-[var(--ink)]">{club.name}</p>
                  <p className="text-xs text-[var(--ink-soft)]">{club.playerNames.join("・")}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      ))}
      {filteredGroups.length === 0 && (
        <p className="mt-6 text-sm text-[var(--ink-soft)]">
          「{query}」に一致するクラブが見つかりませんでした。
        </p>
      )}
    </div>
  );
}
