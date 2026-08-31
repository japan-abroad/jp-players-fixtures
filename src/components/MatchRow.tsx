import Image from "next/image";
import Link from "next/link";
import type { Match } from "@/lib/data";
import { toJstTime } from "@/lib/time";
import { translateTeamName } from "@/lib/teamNames";
import { translatePlayerName } from "@/lib/playerNames";
import { countryColor } from "@/lib/countryStyle";

const STATUS_LABEL_JA: Record<string, string> = {
  POSTPONED: "延期",
  CANCELLED: "中止",
};

export default function MatchRow({ match }: { match: Match }) {
  const isJp = match.jp_players.length > 0;
  const hasScore = match.status === "RESULT" && match.home_score !== null && match.away_score !== null;
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
        {hasScore ? "終了" : STATUS_LABEL_JA[match.status] ?? toJstTime(match.kickoff_utc)}
      </div>

      <div className="matchup min-w-0">
        <div className="team team-home">
          {match.home_logo && <Image src={match.home_logo} alt="" width={22} height={22} unoptimized />}
          <span>{translateTeamName(match.home_team)}</span>
        </div>
        {hasScore ? (
          <span className="score">
            {match.home_score}
            <span className="score-sep">-</span>
            {match.away_score}
          </span>
        ) : (
          <span className="vs">vs</span>
        )}
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
