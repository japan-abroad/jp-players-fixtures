import Link from "next/link";

export default function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-[var(--line)] bg-[var(--paper)]/95 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-baseline gap-2">
          <span className="font-display text-xl font-bold uppercase tracking-tight text-[var(--samurai)]">
            Japan Abroad
          </span>
          <span className="hidden text-sm text-[var(--ink-soft)] sm:inline">
            日本人選手フットボール便
          </span>
        </Link>
        <nav className="flex items-center gap-4 text-sm font-medium text-[var(--ink-soft)]">
          <Link href="/" className="hover:text-[var(--samurai)]">
            試合日程
          </Link>
          <Link href="/clubs" className="hover:text-[var(--samurai)]">
            クラブ一覧
          </Link>
        </nav>
      </div>
    </header>
  );
}
