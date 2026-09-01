import type { MetadataRoute } from "next";
import { getClubs, getAllPlayers } from "@/lib/data";

export const dynamic = "force-static";

const SITE_URL = "https://japan-abroad.github.io/jp-players-fixtures";

export default function sitemap(): MetadataRoute.Sitemap {
  const clubs = getClubs();
  const players = getAllPlayers();

  return [
    { url: `${SITE_URL}/`, changeFrequency: "hourly", priority: 1 },
    { url: `${SITE_URL}/clubs/`, changeFrequency: "daily", priority: 0.8 },
    ...clubs.map((c) => ({
      url: `${SITE_URL}/clubs/${c.team_id}/`,
      changeFrequency: "daily" as const,
      priority: 0.6,
    })),
    ...players.map((p) => ({
      url: `${SITE_URL}/players/${p.slug}/`,
      changeFrequency: "daily" as const,
      priority: 0.5,
    })),
  ];
}
