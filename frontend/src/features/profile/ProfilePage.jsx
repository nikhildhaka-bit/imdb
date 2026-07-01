import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../shared/api";
import { gradientFor } from "../../shared/gradient";
import { useAuth } from "../auth/AuthContext";

const POSTER_BASE = "https://image.tmdb.org/t/p/w92";
const TABS = [
  { key: "ratings", label: "Ratings" },
  { key: "reviews", label: "Reviews" },
];

export default function ProfilePage() {
  const { user } = useAuth();
  const [tab, setTab] = useState("ratings");

  const { data: profile } = useQuery({
    queryKey: ["profile-stats"],
    queryFn: () => api.get("/me").then((r) => r.data),
  });

  const { data: ratings } = useQuery({
    queryKey: ["my-ratings"],
    queryFn: () => api.get("/me/ratings").then((r) => r.data),
    enabled: tab === "ratings",
  });

  const { data: reviews } = useQuery({
    queryKey: ["my-reviews"],
    queryFn: () => api.get("/me/reviews").then((r) => r.data),
    enabled: tab === "reviews",
  });

  if (!profile) return <div className="h-96 bg-surface-2 animate-pulse" />;

  return (
    <div>
      <div className="px-8 md:px-12 py-11 flex items-center gap-6 border-b border-white/[0.07] flex-wrap">
        <div
          className="w-[88px] h-[88px] rounded-full flex items-center justify-center font-extrabold text-[34px] text-white flex-none"
          style={{ background: "linear-gradient(140deg,#3a2452,#e11d2e)" }}
        >
          {user.display_name?.[0]?.toUpperCase()}
        </div>
        <div className="flex-1 min-w-[200px]">
          <div className="font-black text-3xl text-ink tracking-tight">{user.display_name}</div>
          <div className="font-mono text-xs text-muted mt-1.5">member since {profile.member_since}</div>
        </div>
        <div className="flex gap-8">
          <Stat label="Rated" value={profile.rated_count} />
          <Stat label="Reviews" value={profile.review_count} />
          <Stat label="Watchlist" value={profile.watchlist_count} />
        </div>
      </div>

      <div className="px-8 md:px-12 py-8 flex flex-col md:flex-row gap-10">
        <div className="w-full md:w-[300px] flex-none">
          <div className="font-extrabold text-base text-ink mb-4">Your taste</div>
          <div className="flex flex-col gap-3.5">
            {profile.taste.length === 0 && <div className="text-sm text-faint">Rate some movies to see your taste profile.</div>}
            {profile.taste.map((t) => (
              <div key={t.genre}>
                <div className="flex justify-between text-[13px] mb-1.5">
                  <span className="font-semibold text-[#d4d4dc]">{t.genre}</span>
                  <span className="font-mono text-[11.5px] text-muted">{t.count}</span>
                </div>
                <div className="h-[7px] rounded-full bg-[#1a1a20] overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${t.pct}%`, background: "linear-gradient(90deg,#e11d2e,#f5c518)" }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex-1">
          <div className="flex gap-5.5 border-b border-white/[0.08] mb-5">
            {TABS.map((t) => (
              <button
                key={t.key}
                onClick={() => setTab(t.key)}
                className={`font-bold text-sm pb-3 border-b-2 ${
                  tab === t.key ? "text-ink border-crimson" : "text-muted border-transparent"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {tab === "ratings" && (
            <div className="flex flex-col gap-2.5">
              {ratings?.items.length === 0 && <div className="text-sm text-faint">No ratings yet.</div>}
              {ratings?.items.map((r) => (
                <Link
                  key={r.movie_id}
                  to={`/movie/${r.movie_id}`}
                  className="flex items-center gap-4 px-3.5 py-[11px] rounded-xl bg-surface-2 border border-white/5"
                >
                  <div className="w-[42px] h-[63px] rounded-md flex-none border border-white/[0.08] overflow-hidden" style={{ background: gradientFor(r.movie_id) }}>
                    {r.poster_path && <img src={`${POSTER_BASE}${r.poster_path}`} alt="" className="w-full h-full object-cover" />}
                  </div>
                  <div className="flex-1">
                    <div className="font-bold text-[15px] text-ink">{r.title}</div>
                    <div className="font-mono text-[11px] text-faint mt-0.5">{r.year}</div>
                  </div>
                  <div
                    className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-extrabold text-[15px] text-amber"
                    style={{ background: "rgba(245,197,24,0.12)", border: "1px solid rgba(245,197,24,0.3)" }}
                  >
                    ★ {r.score}
                  </div>
                </Link>
              ))}
            </div>
          )}

          {tab === "reviews" && (
            <div className="flex flex-col gap-2.5">
              {reviews?.items.length === 0 && <div className="text-sm text-faint">No reviews yet.</div>}
              {reviews?.items.map((r) => (
                <Link key={r.movie_id} to={`/movie/${r.movie_id}`} className="px-4 py-3.5 rounded-xl bg-surface-2 border border-white/5 block">
                  <div className="font-bold text-[15px] text-ink mb-1.5">{r.title}</div>
                  <p className="text-sm text-muted leading-relaxed">{r.body}</p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="text-center">
      <div className="font-extrabold text-[26px] text-ink">{value}</div>
      <div className="font-mono text-[10px] tracking-[0.1em] uppercase text-faint mt-0.5">{label}</div>
    </div>
  );
}
