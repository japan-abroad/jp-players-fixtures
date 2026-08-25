import fs from "fs";
import path from "path";

export type ClubPlayer = {
  name: string;
  position: string | null;
};

export type Match = {
  fixture_id: number;
  kickoff_utc: string;
  venue: string | null;
  league_name: string;
  round: string | null;
  home_team: string;
  home_logo: string;
  away_team: string;
  away_logo: string;
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
};

const DATA_DIR = path.join(process.cwd(), "data");

function readJson<T>(filename: string, fallback: T): T {
  const filePath = path.join(DATA_DIR, filename);
  if (!fs.existsSync(filePath)) return fallback;
  return JSON.parse(fs.readFileSync(filePath, "utf-8")) as T;
}

export function getFixturesData(): FixturesData {
  return readJson<FixturesData>("fixtures.json", { fetched_at: "", clubs: [] });
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

/** すべての試合をキックオフ日時(UTC)昇順で並べ、所属選手情報も付与したフラットな配列にする */
export type MatchWithClub = Match & { club: Club };

export function getAllMatchesSorted(): MatchWithClub[] {
  const matches: MatchWithClub[] = [];
  for (const club of getClubs()) {
    for (const m of club.matches) {
      matches.push({ ...m, club });
    }
  }
  return matches.sort(
    (a, b) => new Date(a.kickoff_utc).getTime() - new Date(b.kickoff_utc).getTime()
  );
}
