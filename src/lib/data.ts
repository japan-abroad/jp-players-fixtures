import fs from "fs";
import path from "path";

export type ClubPlayer = {
  name: string;
  position: string | null;
};

export type JpPlayerRef = {
  name: string;
  team_id: number;
};

export type Match = {
  fixture_id: string;
  kickoff_utc: string;
  venue: string | null;
  league_name: string;
  country_code: string;
  country_ja: string;
  round: string | null;
  status: "FIXTURE" | "RESULT" | "POSTPONED" | "CANCELLED";
  home_team_id: string;
  home_team: string;
  home_logo: string | null;
  home_score: number | null;
  away_team_id: string;
  away_team: string;
  away_logo: string | null;
  away_score: number | null;
  jp_players: JpPlayerRef[];
};

export type Club = {
  team_id: number;
  team_name: string;
  logo: string;
  league_name: string;
  players: ClubPlayer[];
  matches: Match[];
};

export type FixturesData = {
  fetched_at: string;
  clubs: Club[];
  matches: Match[];
};

const DATA_DIR = path.join(process.cwd(), "data");

function readJson<T>(filename: string, fallback: T): T {
  const filePath = path.join(DATA_DIR, filename);
  if (!fs.existsSync(filePath)) return fallback;
  return JSON.parse(fs.readFileSync(filePath, "utf-8")) as T;
}

export function getFixturesData(): FixturesData {
  return readJson<FixturesData>("fixtures.json", { fetched_at: "", clubs: [], matches: [] });
}

function getHistoryMatches(): Match[] {
  return readJson<{ matches: Match[] }>("fixtures_history.json", { matches: [] }).matches;
}

/** クラブごとに現行fixtures.jsonの試合とfixtures_history.jsonの過去の試合をマージする。
 *  fixtures.jsonは直近±1週間分しか保持しないため、それより前の過去試合結果は
 *  historyから補う(fixture_idで重複排除)。
 *
 *  静的書き出し時にgenerateStaticParams等から選手・クラブの数だけ(数百回)
 *  呼ばれるため、ファイル読み込みとマージ結果をプロセス内でキャッシュする。
 */
let cachedClubs: Club[] | null = null;

export function getClubs(): Club[] {
  if (cachedClubs) return cachedClubs;

  const { clubs } = getFixturesData();
  const history = getHistoryMatches();
  if (history.length === 0) {
    cachedClubs = clubs;
    return cachedClubs;
  }

  cachedClubs = clubs.map((club) => {
    const seen = new Set(club.matches.map((m) => m.fixture_id));
    const historyForClub = history.filter(
      (m) => !seen.has(m.fixture_id) && m.jp_players.some((p) => p.team_id === club.team_id)
    );
    if (historyForClub.length === 0) return club;
    return {
      ...club,
      matches: [...club.matches, ...historyForClub].sort((a, b) =>
        a.kickoff_utc < b.kickoff_utc ? -1 : 1
      ),
    };
  });
  return cachedClubs;
}

export function getClubById(teamId: number): Club | undefined {
  return getClubs().find((c) => c.team_id === teamId);
}

export type PlayerEntry = {
  slug: string;
  name: string;
  position: string | null;
  club: Club;
};

export function getAllPlayers(): PlayerEntry[] {
  const players: PlayerEntry[] = [];
  for (const club of getClubs()) {
    club.players.forEach((p, i) => {
      players.push({
        slug: `${club.team_id}-${i}`,
        name: p.name,
        position: p.position,
        club,
      });
    });
  }
  return players;
}

export function getPlayerBySlug(slug: string): PlayerEntry | undefined {
  return getAllPlayers().find((p) => p.slug === slug);
}

/** 対象リーグの全試合(日本人選手の有無を問わない)をキックオフ日時(UTC)昇順で返す */
export function getAllMatches(): Match[] {
  return getFixturesData().matches;
}
