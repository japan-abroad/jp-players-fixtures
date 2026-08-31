import Image from "next/image";
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

      <div className="matchup min-w-0">
        <div className="team team-home">
          {match.home_logo && <Image src={match.home_logo} alt="" width={22} height={22} unoptimized />}
          <span>{translateTeamName(match.home_team)}</span>
        </div>
        <span className="vs">vs</span>
        <div className="team team-away">
          {match.away_logo && <Image src={match.away_logo} alt="" width={22} height={22} unoptimized />}
          <span>{translateTeamName(match.away_team)}</span>
        </div>
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
