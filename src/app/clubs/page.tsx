import { getClubs, type Club } from "@/lib/data";
import { translateTeamName } from "@/lib/teamNames";
import { SITE_URL, clubsItemListJsonLd } from "@/lib/structuredData";
import ClubsFilterList, { type ClubListItem } from "@/components/ClubsFilterList";

export const metadata = {
  title: "所属クラブ一覧 | 日本人選手フットボール便",
  description:
    "日本人選手が所属する欧州サッカークラブの一覧。リーグごとにクラブを探して、次の試合はいつかをチェックできます。",
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
  const clubs = getClubs();
  const groups = groupClubsByLeague(clubs).map(
    ([leagueName, groupClubs]) =>
      [
        leagueName,
        groupClubs.map((c) => ({
          teamId: c.team_id,
          name: translateTeamName(c.team_name),
          logo: c.logo,
          playerNames: c.players.map((p) => p.name),
        })),
      ] as [string, ClubListItem[]]
  );
  const jsonLd = clubsItemListJsonLd(
    clubs.map((c) => ({ team_id: c.team_id, name: translateTeamName(c.team_name) }))
  );
  return (
    <section className="mx-auto max-w-5xl px-4 py-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <h1 className="font-display text-2xl font-bold uppercase tracking-tight text-[var(--ink)]">
        日本人選手が所属するクラブ
      </h1>
      <ClubsFilterList groups={groups} />
      {groups.length === 0 && (
        <p className="mt-6 text-sm text-[var(--ink-soft)]">データを準備中です。</p>
      )}
    </section>
  );
}
