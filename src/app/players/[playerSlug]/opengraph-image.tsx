import { ImageResponse } from "next/og";
import { getAllPlayers, getPlayerBySlug } from "@/lib/data";
import { translateTeamName } from "@/lib/teamNames";
import { translatePlayerName } from "@/lib/playerNames";

export const dynamic = "force-static";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export function generateStaticParams() {
  return getAllPlayers().map((p) => ({ playerSlug: p.slug }));
}

export default async function OpengraphImage({
  params,
}: {
  params: Promise<{ playerSlug: string }>;
}) {
  const { playerSlug } = await params;
  const player = getPlayerBySlug(playerSlug);
  const playerNameJa = player ? translatePlayerName(player.name) : "日本人選手フットボール便";
  const clubLine = player
    ? `${translateTeamName(player.club.team_name)}${player.position ? ` ・ ${player.position}` : ""}`
    : "";

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "80px",
          background: "linear-gradient(135deg, #10254d 0%, #1b3a78 100%)",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div
            style={{
              width: 48,
              height: 48,
              borderRadius: "50%",
              background: "#f5f6f2",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <div style={{ width: 26, height: 26, borderRadius: "50%", background: "#b3123c" }} />
          </div>
          <span style={{ fontSize: 26, fontWeight: 700, color: "#c7cee0", letterSpacing: 2 }}>
            JAPAN ABROAD
          </span>
        </div>
        <div style={{ display: "flex", marginTop: 48, fontSize: 72, fontWeight: 700, color: "#ffffff" }}>
          {playerNameJa}
        </div>
        {clubLine && (
          <div style={{ display: "flex", marginTop: 20, fontSize: 32, color: "#c7cee0" }}>
            {clubLine}
          </div>
        )}
      </div>
    ),
    { ...size }
  );
}
