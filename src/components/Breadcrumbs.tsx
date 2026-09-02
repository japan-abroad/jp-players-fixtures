import Link from "next/link";
import { SITE_URL } from "@/lib/structuredData";

export default function Breadcrumbs({ items }: { items: { name: string; url: string }[] }) {
  return (
    <nav aria-label="パンくずリスト" className="mx-auto max-w-5xl px-4 pt-4 text-xs text-[var(--ink-soft)]">
      <ol className="flex flex-wrap items-center gap-1">
        {items.map((item, i) => {
          const isLast = i === items.length - 1;
          const href = item.url.replace(SITE_URL, "") || "/";
          return (
            <li key={item.url} className="flex items-center gap-1">
              {i > 0 && <span aria-hidden="true">/</span>}
              {isLast ? (
                <span className="font-semibold text-[var(--ink)]">{item.name}</span>
              ) : (
                <Link href={href} className="hover:text-[var(--samurai)] hover:underline">
                  {item.name}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
