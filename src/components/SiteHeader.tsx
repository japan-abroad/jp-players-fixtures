import Link from "next/link";

export default function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-[var(--line)] bg-[var(--paper)]/95 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-3 px-4 py-3">
        <Link href="/" className="flex items-baseline gap-2">
          <span className="font-display whitespace-nowrap text-lg font-bold uppercase tracking-tight text-[var(--samurai)] sm:text-xl">
            Japan Abroad
          </span>
          <span className="hidden text-sm text-[var(--ink-soft)] sm:inline">
            日本人選手フットボール便
          </span>
        </Link>
        <nav className="flex items-center gap-2.5 text-xs font-medium sm:gap-3 sm:text-sm text-[var(--ink-soft)]">
          <Link href="/" className="whitespace-nowrap py-3 hover:text-[var(--samurai)]">
            試合日程
          </Link>
          <Link href="/jleague" className="whitespace-nowrap py-3 hover:text-[var(--samurai)]">
            Jリーグ
          </Link>
          <Link href="/clubs" className="whitespace-nowrap py-3 hover:text-[var(--samurai)]">
            クラブ<span className="hidden sm:inline">一覧</span>
          </Link>
          <Link href="/players" className="whitespace-nowrap py-3 hover:text-[var(--samurai)]">
            選手<span className="hidden sm:inline">一覧</span>
          </Link>
        </nav>
      </div>
    </header>
  );
}
