import { ImageResponse } from "next/og";

export const dynamic = "force-static";
export const alt = "日本人選手フットボール便 | 欧州サッカー試合日程";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
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
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: "50%",
              background: "#f5f6f2",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <div style={{ width: 34, height: 34, borderRadius: "50%", background: "#b3123c" }} />
          </div>
          <span style={{ fontSize: 34, fontWeight: 700, color: "#ffffff", letterSpacing: 2 }}>
            JAPAN ABROAD
          </span>
        </div>
        <div style={{ display: "flex", marginTop: 56, fontSize: 64, fontWeight: 700, color: "#ffffff" }}>
          日本人選手フットボール便
        </div>
        <div style={{ display: "flex", marginTop: 24, fontSize: 30, color: "#c7cee0" }}>
          欧州サッカークラブに所属する日本人選手の試合日程を日本時間でチェック
        </div>
      </div>
    ),
    { ...size }
  );
}
