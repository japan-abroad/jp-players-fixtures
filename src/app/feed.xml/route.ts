import { getAllMatches, getFixturesData } from "@/lib/data";
import { translateTeamName } from "@/lib/teamNames";
import { translatePlayerName } from "@/lib/playerNames";
import { SITE_URL } from "@/lib/structuredData";

export const dynamic = "force-static";

function escapeXml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export function GET() {
  const matches = getAllMatches();
  const { fetched_at } = getFixturesData();

  const upcoming = matches
    .filter((m) => m.jp_players.length > 0 && new Date(m.kickoff_utc).getTime() >= Date.now())
    .slice(0, 50);

  const items = upcoming
    .map((m) => {
      const homeJa = translateTeamName(m.home_team);
      const awayJa = translateTeamName(m.away_team);
      const players = m.jp_players.map((p) => translatePlayerName(p.name)).join("・");
      const title = `${homeJa} vs ${awayJa}（${m.league_name}）`;
      const link = `${SITE_URL}/#match-${m.fixture_id}`;
      const pubDate = new Date(m.kickoff_utc).toUTCString();
      return `    <item>
      <title>${escapeXml(title)}</title>
      <link>${escapeXml(link)}</link>
      <guid>${escapeXml(link)}</guid>
      <pubDate>${pubDate}</pubDate>
      <description>${escapeXml(`出場が見込まれる日本人選手: ${players}`)}</description>
    </item>`;
    })
    .join("\n");

  const lastBuildDate = fetched_at ? new Date(fetched_at).toUTCString() : new Date().toUTCString();

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>日本人選手フットボール便</title>
    <link>${SITE_URL}/</link>
    <description>欧州サッカークラブに所属する日本人選手の次の試合はいつ？日本時間での試合日程をまとめてチェック。</description>
    <language>ja</language>
    <lastBuildDate>${lastBuildDate}</lastBuildDate>
${items}
  </channel>
</rss>
`;

  return new Response(xml, {
    headers: { "Content-Type": "application/rss+xml; charset=utf-8" },
  });
}
