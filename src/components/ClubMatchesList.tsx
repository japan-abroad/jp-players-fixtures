"use client";

import { useMemo, useState } from "react";
import type { Match } from "@/lib/data";
import { toJstDateLabel } from "@/lib/time";
import { groupMatchesByDate } from "@/lib/matches";
import MatchRow from "./MatchRow";

export default function ClubMatchesList({ matches }: { matches: Match[] }) {
  const [showPast, setShowPast] = useState(false);

  const groups = useMemo(() => groupMatchesByDate(matches, showPast), [matches, showPast]);

  return (
    <div>
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

      <div className="mt-4">
        {groups.map(([dateKey, dayMatches]) => (
          <div key={dateKey}>
            <h2 className="date-heading">{toJstDateLabel(dayMatches[0].kickoff_utc)}</h2>
            {dayMatches.map((m) => (
              <MatchRow key={m.fixture_id} match={m} />
            ))}
          </div>
        ))}
        {groups.length === 0 && (
          <p className="text-sm text-[var(--ink-soft)]">
            {showPast ? "過去の試合結果がありません。" : "今後の試合予定がありません。"}
          </p>
        )}
      </div>
    </div>
  );
}
