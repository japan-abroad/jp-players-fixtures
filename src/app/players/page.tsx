import { getAllPlayers, type PlayerEntry } from "@/lib/data";
import { translateTeamName } from "@/lib/teamNames";
import { translatePlayerName } from "@/lib/playerNames";
import { SITE_URL } from "@/lib/structuredData";
import PlayersFilterList, { type PlayerListItem } from "@/components/PlayersFilterList";

export const metadata = {
  title: "日本人選手一覧 | 日本人選手フットボール便",
  description:
    "欧州サッカークラブに所属する日本人選手(海外組)の一覧。選手ごとの次の試合はいつかを日本時間でチェックできます。",
  alternates: {
    canonical: `${SITE_URL}/players/`,
  },
};

// クラブ一覧と同じ優先順で、所属クラブのリーグごとに選手をグルーピングする。
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

function groupPlayersByLeague(players: PlayerEntry[]): [string, PlayerEntry[]][] {
  const map = new Map<string, PlayerEntry[]>();
  for (const p of players) {
    const league = p.club.league_name;
    if (!map.has(league)) map.set(league, []);
    map.get(league)!.push(p);
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

export default function PlayersPage() {
  const players = getAllPlayers();
  const groups = groupPlayersByLeague(players).map(
    ([leagueName, groupPlayers]) =>
      [
        leagueName,
        groupPlayers.map((p) => ({
          slug: p.slug,
          name: translatePlayerName(p.name),
          teamName: translateTeamName(p.club.team_name),
        })),
      ] as [string, PlayerListItem[]]
  );
  const playerJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: players.map((p, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: translatePlayerName(p.name),
      url: `${SITE_URL}/players/${p.slug}/`,
    })),
  };

  return (
    <section className="mx-auto max-w-5xl px-4 py-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(playerJsonLd) }}
      />
      <h1 className="font-display text-2xl font-bold uppercase tracking-tight text-[var(--ink)]">
        日本人選手一覧
      </h1>
      <PlayersFilterList groups={groups} />
      {groups.length === 0 && (
        <p className="mt-6 text-sm text-[var(--ink-soft)]">データを準備中です。</p>
      )}
    </section>
  );
}
