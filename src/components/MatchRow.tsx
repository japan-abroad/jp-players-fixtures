import Link from "next/link";
import type { Match } from "@/lib/data";
import { toJstTime } from "@/lib/time";
import { translateTeamName } from "@/lib/teamNames";
import { translateVenueName } from "@/lib/venueNames";
import { countryColor, countryFlag } from "@/lib/countryStyle";

export default function MatchRow({ match }: { match: Match }) {
  const isJp = match.jp_players.length > 0;
  return (
    <div
      className="match-row"
      data-jp={isJp ? "true" : "false"}
      data-country={match.country_code}
      id={`match-${match.fixture_id}`}
    >
      <div className="font-mono text-[0.9375rem] font-bold text-[var(--samurai)] tabular-nums">
        {toJstTime(match.kickoff_utc)}
      </div>
      <div className="text-sm font-semibold text-[var(--ink)]">
        {translateTeamName(match.home_team)} vs {translateTeamName(match.away_team)}
        <div className="mt-1 flex flex-wrap items-center gap-1.5">
          <span
            className="country-chip"
            style={{ backgroundColor: countryColor(match.country_code) }}
          >
            {countryFlag(match.country_code)} {match.country_ja}
          </span>
          {match.venue && (
            <span className="text-[0.6875rem] text-[var(--ink-soft)]">
              / {translateVenueName(match.venue)}
            </span>
          )}
        </div>
      </div>
      <div className="flex flex-col items-end gap-0.5">
        {match.jp_players.map((p) => (
          <Link
            key={p.name}
            href={`/clubs/${p.team_id}/`}
            className="jp-player-badge hover:text-[var(--samurai)]"
          >
            {p.name}
          </Link>
        ))}
      </div>
    </div>
  );
}
