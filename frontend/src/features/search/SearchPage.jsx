import { useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../shared/api";
import { gradientFor } from "../../shared/gradient";
import { resultPath } from "../../shared/mediaPath";
import { GridSkeleton } from "../../shared/ui/Skeleton";

const POSTER_BASE = "https://image.tmdb.org/t/p/w342";
const PROFILE_BASE = "https://image.tmdb.org/t/p/w185";

const TABS = [
  { key: "all", label: "All" },
  { key: "movie", label: "Movies" },
  { key: "person", label: "People" },
];

export default function SearchPage() {
  const [params] = useSearchParams();
  const q = params.get("q") ?? "";
  const [tab, setTab] = useState("all");

  const { data, isLoading } = useQuery({
    queryKey: ["search", q],
    queryFn: () => api.get("/search", { params: { q } }).then((r) => r.data),
    enabled: q.length > 0,
    staleTime: 30_000,
  });

  const items = (data?.items ?? []).filter((i) => tab === "all" || i.media_type === tab);

  return (
    <div className="px-8 md:px-12 py-7 flex flex-col gap-6">
      <div className="flex items-baseline gap-3 flex-wrap">
        <span className="font-extrabold text-[22px] text-ink">Results for “{q}”</span>
        {data && <span className="font-mono text-xs text-faint">{data.total} titles</span>}
        <div className="flex-1" />
        <div className="flex gap-2">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`h-8 px-3.5 rounded-lg font-semibold text-[12.5px] ${
                tab === t.key ? "bg-crimson text-white" : "bg-surface-2 border border-white/10 text-muted"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <GridSkeleton />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-[18px]">
          {items.map((item) => (
            <Link key={`${item.media_type}-${item.id}`} to={resultPath(item)}>
              <div
                className="relative w-full aspect-[2/3] rounded-[10px] overflow-hidden border border-white/[0.08] flex items-end p-[11px] box-border cursor-pointer transition-transform duration-200 hover:-translate-y-2 hover:scale-[1.02]"
                style={{ background: gradientFor(item.id) }}
              >
                {item.poster_path && (
                  <img
                    src={`${item.media_type === "person" ? PROFILE_BASE : POSTER_BASE}${item.poster_path}`}
                    alt={item.title}
                    className="absolute inset-0 w-full h-full object-cover"
                  />
                )}
                <div
                  className="absolute inset-0"
                  style={{ backgroundImage: "linear-gradient(180deg, transparent 45%, rgba(0,0,0,0.55))" }}
                />
                {item.rating != null && (
                  <div className="absolute top-[9px] right-[9px] inline-flex items-center gap-[3px] bg-black/70 rounded-md px-[7px] py-[3px] font-bold text-[11px] text-amber">
                    ★ {item.rating.toFixed(1)}
                  </div>
                )}
                <div className="relative font-extrabold text-sm leading-tight text-white/95 [text-shadow:0_2px_10px_rgba(0,0,0,.7)]">
                  {item.title}
                </div>
              </div>
              <div className="font-mono text-[11px] text-faint mt-2">{item.year ?? item.meta}</div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
