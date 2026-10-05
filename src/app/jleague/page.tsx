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

      <a
        href="https://jleagueyosou.blog.fc2.com/"
        className="mt-8 flex max-w-[480px] items-center gap-3.5 rounded-[10px] border border-[var(--line)] bg-[var(--paper-raised)] py-3 pl-3 pr-4 text-[var(--ink)] transition-colors hover:border-[var(--samurai)] focus-visible:border-[var(--samurai)]"
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={`${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/images/usachamo.png`}
          alt="うさちゃも"
          width={64}
          height={64}
          className="h-16 w-16 flex-none rounded-full bg-[#fbf3d9] object-cover"
        />
        <span className="flex min-w-0 flex-1 flex-col gap-0.5">
          <span className="text-[11px] tracking-wider text-[var(--ink-soft)]">関連サイト</span>
          <span className="text-base font-bold text-[var(--samurai)]">全ツッパうさちゃも</span>
          <span className="text-xs text-[var(--ink-soft)]">J1・J2の勝敗をAIで予想するブログ</span>
        </span>
        <span aria-hidden="true" className="flex-none text-2xl text-[var(--ink-soft)]">
          ›
        </span>
      </a>
    </section>
  );
}
