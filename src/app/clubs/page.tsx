import Image from "next/image";
import Link from "next/link";
import { getClubs } from "@/lib/data";

export const metadata = {
  title: "所属クラブ一覧 | 日本人選手フットボール便",
};

export default function ClubsPage() {
  const clubs = getClubs();
  return (
    <section className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="font-display text-2xl font-bold uppercase tracking-tight text-[var(--ink)]">
        日本人選手が所属するクラブ
      </h1>
      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {clubs.map((club) => (
          <Link
            key={club.team_id}
            href={`/clubs/${club.team_id}/`}
            className="flex items-center gap-3 rounded-md border border-[var(--line)] bg-[var(--paper-raised)] p-4 shadow-sm transition hover:border-[var(--samurai)]"
          >
            <Image src={club.logo} alt="" width={40} height={40} unoptimized />
            <div>
              <p className="font-semibold text-[var(--ink)]">{club.team_name}</p>
              <p className="text-xs text-[var(--ink-soft)]">
                {club.league_name} ・ {club.players.map((p) => p.name).join("・")}
              </p>
            </div>
          </Link>
        ))}
        {clubs.length === 0 && (
          <p className="text-sm text-[var(--ink-soft)]">データを準備中です。</p>
        )}
      </div>
    </section>
  );
}
