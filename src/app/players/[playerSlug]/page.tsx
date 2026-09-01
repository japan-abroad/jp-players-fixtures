import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import ClubMatchesList from "@/components/ClubMatchesList";
import { getAllPlayers, getPlayerBySlug } from "@/lib/data";
import { translateTeamName } from "@/lib/teamNames";
import { translatePlayerName } from "@/lib/playerNames";
import { matchesToSportsEventJsonLd, SITE_URL } from "@/lib/structuredData";

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
  const playerNameJa = translatePlayerName(player.name);
  return {
    title: `${playerNameJa}の試合予定 | 日本人選手フットボール便`,
    description: `${clubNameJa}(${player.club.league_name})所属 ${playerNameJa}の直近の試合予定を日本時間で表示。`,
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

  const upcomingForJsonLd = player.club.matches.filter(
    (m) => new Date(m.kickoff_utc).getTime() >= Date.now()
  );
  const jsonLd = matchesToSportsEventJsonLd(
    upcomingForJsonLd,
    `${SITE_URL}/players/${player.slug}/`
  );

  return (
    <div>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <div className="flap">
        <div className="mx-auto flex max-w-5xl items-center gap-4 px-4 py-8">
          <Image src={player.club.logo} alt="" width={56} height={56} unoptimized />
          <div>
            <p className="text-xs uppercase tracking-widest text-white/70">
              {translateTeamName(player.club.team_name)} ・ {player.position ?? ""}
            </p>
            <h1 className="font-display text-3xl font-bold text-white">
              {translatePlayerName(player.name)}
            </h1>
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
          試合日程
        </h2>
        <div className="mt-4">
          <ClubMatchesList matches={player.club.matches} />
        </div>
      </section>
    </div>
  );
}
