import { ImageResponse } from "next/og";

export const dynamic = "force-static";

export function GET() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#1b3a78",
        }}
      >
        <div
          style={{
            width: "75%",
            height: "75%",
            borderRadius: "50%",
            background: "#f5f6f2",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div style={{ width: "40%", height: "40%", borderRadius: "50%", background: "#b3123c" }} />
        </div>
      </div>
    ),
    { width: 512, height: 512 }
  );
}
