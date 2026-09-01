import type { Metadata } from "next";
import { Oswald, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";

const display = Oswald({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-display",
});

const body = Inter({
  subsets: ["latin"],
  variable: "--font-body",
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["500", "700"],
  variable: "--font-mono",
});

const SITE_URL = "https://japan-abroad.github.io/jp-players-fixtures";
const TITLE = "日本人選手フットボール便 | 欧州サッカー試合日程";
const DESCRIPTION =
  "欧州サッカークラブに所属する日本人選手の直近の試合予定を日本時間でまとめてチェックできるサイト。";

export const metadata: Metadata = {
  // basePath("/jp-players-fixtures")はNext.jsがog:image等の相対パス解決時に
  // 自動で付与するため、metadataBaseにはオリジンのみを指定する
  // (SITE_URLをそのまま渡すとbasePathが二重に付いてしまう)。
  metadataBase: new URL(new URL(SITE_URL).origin),
  title: TITLE,
  description: DESCRIPTION,
  openGraph: {
    title: TITLE,
    description: DESCRIPTION,
    url: SITE_URL,
    siteName: "日本人選手フットボール便",
    locale: "ja_JP",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ja">
      <body
        className={`${display.variable} ${body.variable} ${mono.variable} font-body antialiased`}
      >
        <div className="flex min-h-screen flex-col">
          <SiteHeader />
          <main className="flex-1">{children}</main>
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
