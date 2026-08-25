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

      <div className="mt-6">
        <MatchesList matches={matches} />
      </div>
      <AffiliateSlot context="home" />
    </section>
  );
}
