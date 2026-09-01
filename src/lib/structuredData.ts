import type { Match } from "./data";
import { translateTeamName } from "./teamNames";

const SITE_URL = "https://japan-abroad.github.io/jp-players-fixtures";

const EVENT_STATUS: Record<Match["status"], string> = {
  FIXTURE: "https://schema.org/EventScheduled",
  RESULT: "https://schema.org/EventScheduled",
  POSTPONED: "https://schema.org/EventPostponed",
  CANCELLED: "https://schema.org/EventCancelled",
};

/** 試合一覧をschema.org SportsEvent形式のJSON-LDに変換する。
 *  Googleの検索結果でリッチな表示につながる可能性のある構造化データ。
 */
export function matchesToSportsEventJsonLd(matches: Match[], pageUrl: string) {
  return matches.map((m) => {
    const homeJa = translateTeamName(m.home_team);
    const awayJa = translateTeamName(m.away_team);
    return {
      "@context": "https://schema.org",
      "@type": "SportsEvent",
      name: `${homeJa} vs ${awayJa}`,
      startDate: m.kickoff_utc,
      eventStatus: EVENT_STATUS[m.status],
      eventAttendanceMode: "https://schema.org/OfflineEventAttendanceMode",
      sport: "Soccer",
      // locationはGoogleの構造化データで必須項目。goal.com側で会場情報が
      // 取得できない試合もあるため、その場合は開催国名をフォールバックにする。
      location: { "@type": "Place", name: m.venue ?? (m.country_ja || "未定") },
      homeTeam: { "@type": "SportsTeam", name: homeJa },
      awayTeam: { "@type": "SportsTeam", name: awayJa },
      url: `${pageUrl}#match-${m.fixture_id}`,
    };
  });
}

/** パンくずリストのJSON-LD(BreadcrumbList)を生成する。
 *  検索結果にパンくず表示が出る可能性があり、CTR向上を狙う。
 */
export function breadcrumbJsonLd(items: { name: string; url: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: item.name,
      item: item.url,
    })),
  };
}

/** クラブ一覧をschema.org ItemListのJSON-LDに変換する。
 *  一覧ページであることをGoogleに明示し、理解を助ける。
 */
export function clubsItemListJsonLd(clubs: { team_id: number; name: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: clubs.map((c, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: c.name,
      url: `${SITE_URL}/clubs/${c.team_id}/`,
    })),
  };
}

/** 選手ページ用のschema.org Person JSON-LD。
 *  選手個人のエンティティとしての理解をGoogleに促す。
 */
export function playerJsonLd(playerNameJa: string, clubNameJa: string, url: string) {
  return {
    "@context": "https://schema.org",
    "@type": "Person",
    name: playerNameJa,
    memberOf: { "@type": "SportsTeam", name: clubNameJa },
    url,
  };
}

/** クラブページ用のschema.org SportsTeam JSON-LD。
 *  クラブ・所属選手のエンティティとしての理解をGoogleに促す。
 */
export function clubJsonLd(
  clubNameJa: string,
  logo: string,
  playerNamesJa: string[],
  url: string
) {
  return {
    "@context": "https://schema.org",
    "@type": "SportsTeam",
    name: clubNameJa,
    logo,
    sport: "Soccer",
    athlete: playerNamesJa.map((name) => ({ "@type": "Person", name })),
    url,
  };
}

export { SITE_URL };
