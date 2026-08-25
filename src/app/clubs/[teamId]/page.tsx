import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import MatchRow from "@/components/MatchRow";
import { getClubById, getClubs, getAllPlayers } from "@/lib/data";
import { translateTeamName } from "@/lib/teamNames";
import { translatePlayerName } from "@/lib/playerNames";

export function generateStaticParams() {
  return getClubs().map((c) => ({ teamId: String(c.team_id) }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ teamId: string }>;
}) {
  const { teamId } = await params;
  const club = getClubById(Number(teamId));
  if (!club) return {};
  const clubNameJa = translateTeamName(club.team_name);
  return {
    title: `${clubNameJa}の試合予定 | 日本人選手フットボール便`,
    description: `${clubNameJa}(${club.league_name})に所属する${club.players
      .map((p) => translatePlayerName(p.name))
      .join("・")}の直近の試合予定。`,
  };
}

export default async function ClubPage({
  params,
}: {
  params: Promise<{ teamId: string }>;
}) {
  const { teamId } = await params;
  const club = getClubById(Number(teamId));
  if (!club) notFound();

  const players = getAllPlayers().filter((p) => p.club.team_id === club.team_id);

  return (
    <div>
      <div className="flap">
        <div className="mx-auto flex max-w-5xl items-center gap-4 px-4 py-8">
          <Image src={club.logo} alt="" width={64} height={64} unoptimized />
          <div>
            <p className="text-xs uppercase tracking-widest text-white/70">{club.league_name}</p>
            <h1 className="font-display text-3xl font-bold text-white">
              {translateTeamName(club.team_name)}
            </h1>
          </div>
        </div>
      </div>

      <section className="mx-auto max-w-5xl px-4 py-8">
        <h2 className="font-display text-lg font-semibold uppercase tracking-tight text-[var(--samurai)]">
          所属する日本人選手
        </h2>
        <div className="mt-3 flex flex-wrap gap-2">
          {players.map((p) => (
            <Link
              key={p.slug}
              href={`/players/${p.slug}/`}
              className="rounded-full bg-[var(--samurai)]/10 px-4 py-1.5 text-sm font-semibold text-[var(--samurai)] hover:bg-[var(--samurai)]/20"
            >
              {translatePlayerName(p.name)}
              {p.position ? ` (${p.position})` : ""}
            </Link>
          ))}
        </div>

        <h2 className="mt-10 border-b border-[var(--line)] pb-2 font-display text-lg font-semibold uppercase tracking-tight text-[var(--ink)]">
          直近の試合予定
        </h2>
        <div className="mt-4">
          {club.matches.map((m) => (
            <MatchRow key={m.fixture_id} match={m} />
          ))}
          {club.matches.length === 0 && (
            <p className="text-sm text-[var(--ink-soft)]">現在表示できる試合がありません。</p>
          )}
        </div>
      </section>
    </div>
  );
}
