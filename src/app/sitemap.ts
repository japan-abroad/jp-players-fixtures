import type { MetadataRoute } from "next";
import { getClubs, getAllPlayers, getFixturesData, type Club } from "@/lib/data";

export const dynamic = "force-static";

const SITE_URL = "https://japan-abroad.github.io/jp-players-fixtures";

// 試合終了からスコアが反映されるまでの目安
const RESULT_SETTLE_MS = 2 * 60 * 60 * 1000;

/** クラブ・選手ページの内容(次の試合・直近結果)が実際に変わるのは試合の終了時。
 *  全URLにビルド時刻(6時間毎に更新)を付けるとGoogleにlastmodを信用されなく
 *  なるため(2026-10-18)、直近に終わった試合のキックオフ+2時間を使う。 */
function clubLastModified(club: Club, fetchedAt: Date | undefined): Date | undefined {
  const finished = club.matches.filter((m) => m.status === "RESULT");
  if (finished.length === 0) return undefined;
  const latestKickoff = Math.max(...finished.map((m) => new Date(m.kickoff_utc).getTime()));
  const settled = latestKickoff + RESULT_SETTLE_MS;
  return new Date(fetchedAt ? Math.min(settled, fetchedAt.getTime()) : settled);
}

export default function sitemap(): MetadataRoute.Sitemap {
  const clubs = getClubs();
  const players = getAllPlayers();
  const { fetched_at } = getFixturesData();
  const lastModified = fetched_at ? new Date(fetched_at) : undefined;

  const clubDates = new Map(clubs.map((c) => [c.team_id, clubLastModified(c, lastModified)]));
  const knownDates = [...clubDates.values()].filter((d): d is Date => d !== undefined);
  const listLastModified =
    knownDates.length > 0 ? new Date(Math.max(...knownDates.map((d) => d.getTime()))) : undefined;

  return [
    { url: `${SITE_URL}/`, changeFrequency: "hourly", priority: 1, lastModified },
    { url: `${SITE_URL}/jleague/`, changeFrequency: "hourly", priority: 0.8, lastModified },
    { url: `${SITE_URL}/clubs/`, changeFrequency: "daily", priority: 0.8, lastModified: listLastModified },
    { url: `${SITE_URL}/players/`, changeFrequency: "daily", priority: 0.8, lastModified: listLastModified },
    ...clubs.map((c) => ({
      url: `${SITE_URL}/clubs/${c.team_id}/`,
      changeFrequency: "daily" as const,
      priority: 0.6,
      lastModified: clubDates.get(c.team_id),
    })),
    ...players.map((p) => ({
      url: `${SITE_URL}/players/${p.slug}/`,
      changeFrequency: "daily" as const,
      priority: 0.5,
      lastModified: clubDates.get(p.club.team_id),
    })),
  ];
}
