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
  fixture_id: number;
  kickoff_utc: string;
  venue: string | null;
  league_name: string;
  country_code: string;
  country_ja: string;
  round: string | null;
  home_team_id: number;
  home_team: string;
  home_logo: string;
  away_team_id: number;
  away_team: string;
  away_logo: string;
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

export function getClubs(): Club[] {
  return getFixturesData().clubs;
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
