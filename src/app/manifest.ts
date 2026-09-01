import type { MetadataRoute } from "next";

export const dynamic = "force-static";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "日本人選手フットボール便",
    short_name: "Japan Abroad",
    description: "欧州サッカークラブに所属する日本人選手の次の試合はいつ？日本時間での試合日程をチェック。",
    start_url: ".",
    display: "standalone",
    background_color: "#f5f6f2",
    theme_color: "#1b3a78",
    icons: [
      { src: "icon-192", sizes: "192x192", type: "image/png" },
      { src: "icon-512", sizes: "512x512", type: "image/png" },
    ],
  };
}
