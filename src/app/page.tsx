import MatchesList from "@/components/MatchesList";
import AffiliateSlot from "@/components/AffiliateSlot";
import { getAllMatches } from "@/lib/data";
import { matchesToSportsEventJsonLd, SITE_URL } from "@/lib/structuredData";

export default function HomePage() {
  const matches = getAllMatches();

  // トップページの初期表示(今後の試合)に合わせて、未来の試合のみを
  // 構造化データとして出力する。上限を設けページ肥大化を防ぐ。
  const upcomingForJsonLd = matches
    .filter((m) => new Date(m.kickoff_utc).getTime() >= Date.now())
    .slice(0, 100);
  const jsonLd = matchesToSportsEventJsonLd(upcomingForJsonLd, `${SITE_URL}/`);

  return (
    <section className="mx-auto max-w-5xl px-4 py-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
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
