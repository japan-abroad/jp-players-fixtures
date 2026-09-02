import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import ClubMatchesList from "@/components/ClubMatchesList";
import Breadcrumbs from "@/components/Breadcrumbs";
import { getClubById, getClubs, getAllPlayers } from "@/lib/data";
import { translateTeamName } from "@/lib/teamNames";
import { translatePlayerName } from "@/lib/playerNames";
import {
  matchesToSportsEventJsonLd,
  breadcrumbJsonLd,
  clubJsonLd,
  SITE_URL,
} from "@/lib/structuredData";

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
  const playerNames = club.players.map((p) => translatePlayerName(p.name)).join("・");
  return {
    title: `${clubNameJa}の次の試合はいつ？日本人選手の出場予定 | 日本人選手フットボール便`,
    description: `${clubNameJa}(${club.league_name})の次の試合はいつ？日本時間の試合日程と、所属する${playerNames}の出場予定をチェック。`,
    alternates: {
      canonical: `${SITE_URL}/clubs/${teamId}/`,
    },
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

  const upcomingForJsonLd = club.matches.filter(
    (m) => new Date(m.kickoff_utc).getTime() >= Date.now()
  );
  const jsonLd = matchesToSportsEventJsonLd(
    upcomingForJsonLd,
    `${SITE_URL}/clubs/${club.team_id}/`
  );
  const clubNameJa = translateTeamName(club.team_name);
  const breadcrumb = breadcrumbJsonLd([
    { name: "試合日程", url: `${SITE_URL}/` },
    { name: "クラブ一覧", url: `${SITE_URL}/clubs/` },
    { name: clubNameJa, url: `${SITE_URL}/clubs/${club.team_id}/` },
  ]);
  const team = clubJsonLd(
    clubNameJa,
    club.logo,
    players.map((p) => translatePlayerName(p.name)),
    `${SITE_URL}/clubs/${club.team_id}/`
  );

  return (
    <div>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(team) }}
      />
      <Breadcrumbs items={breadcrumb.itemListElement.map((i) => ({ name: i.name, url: i.item }))} />
      <div className="flap">
        <div className="mx-auto flex max-w-5xl items-center gap-4 px-4 py-8">
          <Image src={club.logo} alt={clubNameJa} width={64} height={64} unoptimized />
          <div>
            <p className="text-xs uppercase tracking-widest text-white/70">{club.league_name}</p>
            <h1 className="font-display text-3xl font-bold text-white">{clubNameJa}</h1>
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
          試合日程
        </h2>
        <div className="mt-4">
          <ClubMatchesList matches={club.matches} />
        </div>
      </section>
    </div>
  );
}
