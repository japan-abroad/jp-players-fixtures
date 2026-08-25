import MatchesList from "@/components/MatchesList";
import AffiliateSlot from "@/components/AffiliateSlot";
import { getAllMatches } from "@/lib/data";

export default function HomePage() {
  const matches = getAllMatches();

  return (
    <section className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="font-display text-2xl font-bold uppercase tracking-tight text-[var(--ink)]">
        直近の試合予定
      </h1>
      <p className="mt-1 text-sm text-[var(--ink-soft)]">
        対象リーグの試合を日本時間(JST)で表示しています。日本人選手が所属するクラブの試合は選手名を添えて強調しています。
      </p>

      <div className="mt-6">
        <MatchesList matches={matches} />
      </div>
      <AffiliateSlot context="home" />
    </section>
  );
}
