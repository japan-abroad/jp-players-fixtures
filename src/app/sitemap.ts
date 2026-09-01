import type { MetadataRoute } from "next";
import { getClubs, getAllPlayers, getFixturesData } from "@/lib/data";

export const dynamic = "force-static";

const SITE_URL = "https://japan-abroad.github.io/jp-players-fixtures";

export default function sitemap(): MetadataRoute.Sitemap {
  const clubs = getClubs();
  const players = getAllPlayers();
  const { fetched_at } = getFixturesData();
  const lastModified = fetched_at ? new Date(fetched_at) : undefined;

  return [
    { url: `${SITE_URL}/`, changeFrequency: "hourly", priority: 1, lastModified },
    { url: `${SITE_URL}/clubs/`, changeFrequency: "daily", priority: 0.8, lastModified },
    ...clubs.map((c) => ({
      url: `${SITE_URL}/clubs/${c.team_id}/`,
      changeFrequency: "daily" as const,
      priority: 0.6,
      lastModified,
    })),
    ...players.map((p) => ({
      url: `${SITE_URL}/players/${p.slug}/`,
      changeFrequency: "daily" as const,
      priority: 0.5,
      lastModified,
    })),
  ];
}
