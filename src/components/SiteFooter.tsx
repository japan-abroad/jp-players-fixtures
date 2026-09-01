import Link from "next/link";

export default function SiteFooter() {
  return (
    <footer className="border-t border-[var(--line)] py-8 text-center text-xs text-[var(--ink-soft)]">
      <p>
試合データは自動生成しています。出場は監督采配により変わる場合があります。
      </p>
      <p className="mt-2">
        <Link href="/feed.xml" className="hover:text-[var(--samurai)]">
          RSSフィード
        </Link>
      </p>
      <p className="mt-1">© Japan Abroad</p>
    </footer>
  );
}
