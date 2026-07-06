import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../shared/api";
import { gradientFor } from "../../shared/gradient";

const BACKDROP_BASE = "https://image.tmdb.org/t/p/original";
const POSTER_BASE = "https://image.tmdb.org/t/p/w342";
const PROFILE_BASE = "https://image.tmdb.org/t/p/w185";

export default function TvShowDetailPage() {
  const { id } = useParams();
  const tvId = Number(id);

  const { data: show, isLoading } = useQuery({
    queryKey: ["tv", tvId],
    queryFn: () => api.get(`/tv/${tvId}`).then((r) => r.data),
  });

  if (isLoading || !show) {
    return <div className="h-[400px] bg-surface-2 animate-pulse" />;
  }

  return (
    <div className="flex flex-col">
      <div
        className="relative p-11 bg-cover bg-center"
        style={show.backdrop_path ? { backgroundImage: `url(${BACKDROP_BASE}${show.backdrop_path})` } : undefined}
      >
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(90deg,rgba(10,10,13,0.95),rgba(10,10,13,0.6) 55%,rgba(10,10,13,0.35)),linear-gradient(0deg,#0a0a0d,transparent 55%)",
          }}
        />
        <div className="relative flex flex-col md:flex-row gap-9">
          <div
            className="w-[230px] h-[345px] flex-none rounded-xl border border-white/[0.14] shadow-[0_20px_50px_-12px_rgba(0,0,0,0.8)] overflow-hidden"
            style={{ background: gradientFor(show.id) }}
          >
            {show.poster_path && (
              <img src={`${POSTER_BASE}${show.poster_path}`} alt={show.title} className="w-full h-full object-cover" />
            )}
          </div>
          <div className="flex-1 pt-2">
            <div className="font-black text-[42px] leading-none tracking-tight text-white">
              {show.title}{" "}
              {show.first_air_date && (
                <span className="font-medium text-muted">({show.first_air_date.slice(0, 4)})</span>
              )}
            </div>
            <div className="flex items-center gap-3.5 my-4 text-sm text-[#c8c8d0] font-semibold flex-wrap">
              {show.vote_average != null && (
                <span
                  className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-[5px] text-amber"
                  style={{ background: "rgba(245,197,24,0.14)", border: "1px solid rgba(245,197,24,0.35)" }}
                >
                  ★ {show.vote_average.toFixed(1)}
                  <span className="text-[#a89432] font-medium text-xs">/10</span>
                </span>
              )}
              {show.number_of_seasons && (
                <span>
                  {show.number_of_seasons} season{show.number_of_seasons === 1 ? "" : "s"}
                </span>
              )}
              {show.number_of_episodes && <span>{show.number_of_episodes} episodes</span>}
            </div>
            <div className="flex gap-2 mb-5 flex-wrap">
              {show.genres.map((g) => (
                <span key={g.id} className="text-xs font-semibold text-[#d4d4dc] border border-white/[0.16] rounded-full px-3.5 py-[5px]">
                  {g.name}
                </span>
              ))}
            </div>
            {show.overview && <div className="text-[15px] leading-[1.6] text-[#b4b4be] max-w-[640px] mb-6">{show.overview}</div>}

            {show.trailer_key && (
              <a
                href={`https://www.youtube.com/watch?v=${show.trailer_key}`}
                target="_blank"
                rel="noreferrer"
                className="h-11 px-5 rounded-lg bg-crimson inline-flex items-center gap-2 font-bold text-sm text-white"
              >
                ▶ Trailer
              </a>
            )}
          </div>
        </div>
      </div>

      <div className="px-8 md:px-12 py-9 flex flex-col gap-2">
        {show.cast?.length > 0 && (
          <div className="mb-8">
            <div className="font-extrabold text-lg text-ink mb-4">Top billed cast</div>
            <div className="flex gap-4 overflow-x-auto overflow-y-visible py-2.5 no-scrollbar">
              {show.cast.map((c) => (
                <Link key={c.person_id} to={`/person/${c.person_id}`} className="flex-none w-[132px] group">
                  <div
                    className="w-[132px] h-40 rounded-[10px] border border-white/[0.08] overflow-hidden transition-transform duration-200 group-hover:-translate-y-2 group-hover:scale-[1.03]"
                    style={{ background: gradientFor(c.person_id) }}
                  >
                    {c.profile_path && (
                      <img src={`${PROFILE_BASE}${c.profile_path}`} alt={c.name} className="w-full h-full object-cover" />
                    )}
                  </div>
                  <div className="font-bold text-[13.5px] text-ink mt-2.5 leading-tight">{c.name}</div>
                  <div className="text-[12.5px] text-muted mt-0.5 leading-tight">{c.role}</div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
