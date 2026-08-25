import Link from "next/link";
import type { Match } from "@/lib/data";
import { toJstTime } from "@/lib/time";
import { translateTeamName } from "@/lib/teamNames";
import { translatePlayerName } from "@/lib/playerNames";
import { countryColor } from "@/lib/countryStyle";

export default function MatchRow({ match }: { match: Match }) {
  const isJp = match.jp_players.length > 0;
  return (
    <div
      className="match-row"
      data-jp={isJp ? "true" : "false"}
      data-country={match.country_code}
      id={`match-${match.fixture_id}`}
    >
      <span
        className="country-chip shrink-0"
        style={{ backgroundColor: countryColor(match.country_code) }}
      >
        {match.country_ja}
      </span>

      <span className="league-chip shrink-0">{match.league_name}</span>

      <div className="font-mono text-[0.9375rem] font-bold text-[var(--samurai)] tabular-nums shrink-0">
        {toJstTime(match.kickoff_utc)}
      </div>

      <div className="text-sm font-semibold text-[var(--ink)] min-w-0">
        {translateTeamName(match.home_team)} vs {translateTeamName(match.away_team)}
      </div>

      <div className="flex flex-col items-end gap-0.5 shrink-0">
        {match.jp_players.map((p) => (
          <Link
            key={p.name}
            href={`/clubs/${p.team_id}/`}
            className="jp-player-badge hover:text-[var(--samurai)]"
          >
            {translatePlayerName(p.name)}
          </Link>
        ))}
      </div>
    </div>
  );
}
