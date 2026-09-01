import Link from "next/link";

export const metadata = {
  title: "ページが見つかりません | 日本人選手フットボール便",
};

export default function NotFound() {
  return (
    <section className="mx-auto max-w-2xl px-4 py-16 text-center">
      <p className="font-display text-6xl font-bold text-[var(--samurai)]">404</p>
      <h1 className="mt-4 font-display text-xl font-bold uppercase tracking-tight text-[var(--ink)]">
        お探しのページが見つかりませんでした
      </h1>
      <p className="mt-3 text-sm text-[var(--ink-soft)]">
        URLが変更されたか、削除された可能性があります。以下から試合日程・クラブ一覧をご覧ください。
      </p>
      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        <Link
          href="/"
          className="rounded-full bg-[var(--samurai)] px-6 py-2 text-sm font-bold text-white hover:bg-[var(--samurai-deep)]"
        >
          試合日程トップへ戻る
        </Link>
        <Link
          href="/clubs/"
          className="rounded-full border border-[var(--line)] px-6 py-2 text-sm font-bold text-[var(--ink)] hover:border-[var(--samurai)]"
        >
          所属クラブ一覧を見る
        </Link>
      </div>
    </section>
  );
}
