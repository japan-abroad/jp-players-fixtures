import Image from "next/image";
import Link from "next/link";
import type { MatchWithClub } from "@/lib/data";
import { toJstTime, toLocalKickoffLabel } from "@/lib/time";

export default function MatchCard({ match }: { match: MatchWithClub }) {
  return (
    <article
      id={`match-${match.fixture_id}`}
      className="rounded-md border border-[var(--line)] bg-[var(--paper-raised)] p-4 shadow-sm scroll-mt-20"
    >
      <div className="flex items-center justify-between text-xs text-[var(--ink-soft)]">
        <span>
          {match.league_name}
          {match.round ? ` · ${match.round}` : ""}
        </span>
        <span>{match.venue}</span>
      </div>

      <div className="mt-3 flex items-center justify-between gap-4">
        <TeamBlock name={match.home_team} logo={match.home_logo} />
        <div className="flex flex-col items-center">
          <span className="flap-digit font-mono text-2xl font-bold text-[var(--samurai)]">
            {toJstTime(match.kickoff_utc)}
          </span>
          <span className="text-[11px] text-[var(--ink-soft)]">JST</span>
          <span className="mt-1 text-[11px] text-[var(--ink-soft)]">
            現地 {toLocalKickoffLabel(match.kickoff_utc)}
          </span>
        </div>
        <TeamBlock name={match.away_team} logo={match.away_logo} align="right" />
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-[var(--line)] pt-3">
        <span className="text-xs text-[var(--ink-soft)]">出場注目:</span>
        <Link
          href={`/clubs/${match.club.team_id}/`}
          className="rounded-full bg-[var(--pitch)]/10 px-3 py-1 text-xs font-semibold text-[var(--pitch)] hover:bg-[var(--pitch)]/20"
        >
          {match.club.team_name}
        </Link>
        {match.club.players.map((p) => (
          <span
            key={p.name}
            className="rounded-full bg-[var(--samurai)]/10 px-3 py-1 text-xs font-semibold text-[var(--samurai)]"
          >
            {p.name}
          </span>
        ))}
      </div>
    </article>
  );
}

function TeamBlock({
  name,
  logo,
  align = "left",
}: {
  name: string;
  logo: string;
  align?: "left" | "right";
}) {
  return (
    <div
      className={`flex flex-1 items-center gap-2 ${
        align === "right" ? "flex-row-reverse text-right" : ""
      }`}
    >
      <Image src={logo} alt="" width={28} height={28} className="shrink-0" unoptimized />
      <span className="text-sm font-semibold leading-tight text-[var(--ink)]">{name}</span>
    </div>
  );
}
