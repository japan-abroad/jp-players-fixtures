import JleagueMatchesList from "@/components/JleagueMatchesList";
import { getJleagueMatches, getFixturesData } from "@/lib/data";
import { matchesToSportsEventJsonLd, SITE_URL } from "@/lib/structuredData";
import { toJstDateLabel, toJstTime } from "@/lib/time";

export const metadata = {
  title: "Jリーグ 試合日程・結果 | 日本人選手フットボール便",
  description:
    "J1・J2・J3リーグとルヴァンカップ・天皇杯の直近の試合日程と試合結果。キックオフ時刻は日本時間で表示します。",
  alternates: {
    canonical: `${SITE_URL}/jleague/`,
  },
};

export default function JleaguePage() {
  const matches = getJleagueMatches();
  const { fetched_at } = getFixturesData();

  const upcomingForJsonLd = matches
    .filter((m) => new Date(m.kickoff_utc).getTime() >= Date.now())
    .slice(0, 100);
  const jsonLd = matchesToSportsEventJsonLd(upcomingForJsonLd, `${SITE_URL}/jleague/`);

  return (
    <section className="mx-auto max-w-5xl px-4 py-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <h1 className="font-display text-2xl font-bold uppercase tracking-tight text-[var(--ink)]">
        Jリーグの試合予定・結果
      </h1>
      {fetched_at && (
        <p className="mt-1 text-xs text-[var(--ink-soft)]">
          最終更新: {toJstDateLabel(fetched_at)} {toJstTime(fetched_at)}
        </p>
      )}

      <div className="mt-6">
        <JleagueMatchesList matches={matches} />
      </div>
    </section>
  );
}
