import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import MatchRow from "@/components/MatchRow";
import { getAllPlayers, getPlayerBySlug } from "@/lib/data";
import { translateTeamName } from "@/lib/teamNames";

export function generateStaticParams() {
  return getAllPlayers().map((p) => ({ playerSlug: p.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ playerSlug: string }>;
}) {
  const { playerSlug } = await params;
  const player = getPlayerBySlug(playerSlug);
  if (!player) return {};
  const clubNameJa = translateTeamName(player.club.team_name);
  return {
    title: `${player.name}の試合予定 | 日本人選手フットボール便`,
    description: `${clubNameJa}(${player.club.league_name})所属 ${player.name}の直近の試合予定を日本時間で表示。`,
  };
}

export default async function PlayerPage({
  params,
}: {
  params: Promise<{ playerSlug: string }>;
}) {
  const { playerSlug } = await params;
  const player = getPlayerBySlug(playerSlug);
  if (!player) notFound();

  return (
    <div>
      <div className="flap">
        <div className="mx-auto flex max-w-5xl items-center gap-4 px-4 py-8">
          <Image src={player.club.logo} alt="" width={56} height={56} unoptimized />
          <div>
            <p className="text-xs uppercase tracking-widest text-white/70">
              {translateTeamName(player.club.team_name)} ・ {player.position ?? ""}
            </p>
            <h1 className="font-display text-3xl font-bold text-white">{player.name}</h1>
          </div>
        </div>
      </div>

      <section className="mx-auto max-w-5xl px-4 py-8">
        <p className="text-sm text-[var(--ink-soft)]">
          所属クラブ:{" "}
          <Link
            href={`/clubs/${player.club.team_id}/`}
            className="font-semibold text-[var(--samurai)] hover:underline"
          >
            {translateTeamName(player.club.team_name)}
          </Link>
        </p>

        <h2 className="mt-8 border-b border-[var(--line)] pb-2 font-display text-lg font-semibold uppercase tracking-tight text-[var(--ink)]">
          直近の試合予定
        </h2>
        <div className="mt-4">
          {player.club.matches.map((m) => (
            <MatchRow key={m.fixture_id} match={m} />
          ))}
          {player.club.matches.length === 0 && (
            <p className="text-sm text-[var(--ink-soft)]">現在表示できる試合がありません。</p>
          )}
        </div>
      </section>
    </div>
  );
}
