import Image from "next/image";
import Link from "next/link";
import { getClubs, type Club } from "@/lib/data";
import { translateTeamName } from "@/lib/teamNames";
import { SITE_URL } from "@/lib/structuredData";

export const metadata = {
  title: "所属クラブ一覧 | 日本人選手フットボール便",
  alternates: {
    canonical: `${SITE_URL}/clubs/`,
  },
};

// 主要リーグを国順に並べ、それ以外(2部・カップ経由で判明したリーグ等)は
// あいうえお順で末尾にまとめる。
const LEAGUE_ORDER = [
  "プレミアリーグ",
  "ラ・リーガ",
  "ブンデスリーガ",
  "セリエA",
  "リーグ・アン",
  "エールディヴィジ",
  "リーガ・ポルトガル",
  "ベルギー・プロリーグ",
  "スコティッシュ・プレミアシップ",
  "スュペル・リグ",
];

function groupClubsByLeague(clubs: Club[]): [string, Club[]][] {
  const map = new Map<string, Club[]>();
  for (const club of clubs) {
    if (!map.has(club.league_name)) map.set(club.league_name, []);
    map.get(club.league_name)!.push(club);
  }
  const entries = [...map.entries()];
  entries.sort(([a], [b]) => {
    const ai = LEAGUE_ORDER.indexOf(a);
    const bi = LEAGUE_ORDER.indexOf(b);
    if (ai !== -1 && bi !== -1) return ai - bi;
    if (ai !== -1) return -1;
    if (bi !== -1) return 1;
    return a.localeCompare(b, "ja");
  });
  return entries;
}

export default function ClubsPage() {
  const groups = groupClubsByLeague(getClubs());
  return (
    <section className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="font-display text-2xl font-bold uppercase tracking-tight text-[var(--ink)]">
        日本人選手が所属するクラブ
      </h1>
      {groups.map(([leagueName, clubs]) => (
        <div key={leagueName} className="mt-8 first:mt-6">
          <h2 className="font-display text-sm font-bold uppercase tracking-tight text-[var(--samurai)]">
            {leagueName}
          </h2>
          <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
            {clubs.map((club) => (
              <Link
                key={club.team_id}
                href={`/clubs/${club.team_id}/`}
                className="flex items-center gap-3 rounded-md border border-[var(--line)] bg-[var(--paper-raised)] p-4 shadow-sm transition hover:border-[var(--samurai)]"
              >
                <Image
                  src={club.logo}
                  alt={translateTeamName(club.team_name)}
                  width={40}
                  height={40}
                  unoptimized
                />
                <div>
                  <p className="font-semibold text-[var(--ink)]">
                    {translateTeamName(club.team_name)}
                  </p>
                  <p className="text-xs text-[var(--ink-soft)]">
                    {club.players.map((p) => p.name).join("・")}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      ))}
      {groups.length === 0 && (
        <p className="mt-6 text-sm text-[var(--ink-soft)]">データを準備中です。</p>
      )}
    </section>
  );
}
