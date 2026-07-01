import { useParams, Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../shared/api";
import { gradientFor } from "../../shared/gradient";
import { useAuth } from "../auth/AuthContext";
import Rail from "../../shared/ui/Rail";
import RatingWidget from "./RatingWidget";
import Reviews from "./Reviews";

const BACKDROP_BASE = "https://image.tmdb.org/t/p/original";
const POSTER_BASE = "https://image.tmdb.org/t/p/w342";
const PROFILE_BASE = "https://image.tmdb.org/t/p/w185";

export default function MovieDetailPage() {
  const { id } = useParams();
  const movieId = Number(id);
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();

  const { data: movie, isLoading } = useQuery({
    queryKey: ["movie", movieId],
    queryFn: () => api.get(`/movies/${movieId}`).then((r) => r.data),
  });

  const { data: similar } = useQuery({
    queryKey: ["similar", movieId],
    queryFn: () => api.get(`/movies/${movieId}/similar`).then((r) => r.data),
    enabled: Boolean(movie),
  });

  const invalidateMovie = () => {
    queryClient.invalidateQueries({ queryKey: ["movie", movieId] });
    queryClient.invalidateQueries({ queryKey: ["me"] });
  };

  const rateMutation = useMutation({
    mutationFn: (score) => api.put(`/movies/${movieId}/rating`, { score }),
    onSuccess: invalidateMovie,
  });
  const clearRatingMutation = useMutation({
    mutationFn: () => api.delete(`/movies/${movieId}/rating`),
    onSuccess: invalidateMovie,
  });
  const watchlistMutation = useMutation({
    mutationFn: () =>
      movie.in_watchlist ? api.delete(`/me/watchlist/${movieId}`) : api.put(`/me/watchlist/${movieId}`),
    onSuccess: invalidateMovie,
  });

  if (isLoading || !movie) {
    return <div className="h-[400px] bg-surface-2 animate-pulse" />;
  }

  return (
    <div className="flex flex-col">
      <div
        className="relative p-11 bg-cover bg-center"
        style={movie.backdrop_path ? { backgroundImage: `url(${BACKDROP_BASE}${movie.backdrop_path})` } : undefined}
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
            style={{ background: gradientFor(movie.id) }}
          >
            {movie.poster_path && (
              <img src={`${POSTER_BASE}${movie.poster_path}`} alt={movie.title} className="w-full h-full object-cover" />
            )}
          </div>
          <div className="flex-1 pt-2">
            <div className="font-black text-[42px] leading-none tracking-tight text-white">
              {movie.title}{" "}
              {movie.release_date && (
                <span className="font-medium text-muted">({movie.release_date.slice(0, 4)})</span>
              )}
            </div>
            <div className="flex items-center gap-3.5 my-4 text-sm text-[#c8c8d0] font-semibold flex-wrap">
              {movie.vote_average != null && (
                <span
                  className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-[5px] text-amber"
                  style={{ background: "rgba(245,197,24,0.14)", border: "1px solid rgba(245,197,24,0.35)" }}
                >
                  ★ {movie.vote_average.toFixed(1)}
                  <span className="text-[#a89432] font-medium text-xs">/10</span>
                </span>
              )}
              {movie.runtime && (
                <span>
                  {Math.floor(movie.runtime / 60)}h {movie.runtime % 60}m
                </span>
              )}
              {movie.release_date && <span>{movie.release_date.slice(0, 4)}</span>}
            </div>
            <div className="flex gap-2 mb-5 flex-wrap">
              {movie.genres.map((g) => (
                <span key={g.id} className="text-xs font-semibold text-[#d4d4dc] border border-white/[0.16] rounded-full px-3.5 py-[5px]">
                  {g.name}
                </span>
              ))}
            </div>
            {movie.overview && <div className="text-[15px] leading-[1.6] text-[#b4b4be] max-w-[640px] mb-6">{movie.overview}</div>}

            <div className="flex items-center gap-4 flex-wrap">
              {isAuthenticated ? (
                <RatingWidget
                  value={movie.my_rating}
                  onRate={(score) => rateMutation.mutate(score)}
                  onClear={() => clearRatingMutation.mutate()}
                />
              ) : (
                <Link to="/login" className="font-mono text-xs text-muted underline">
                  Sign in to rate
                </Link>
              )}
              <div className="w-px h-11 bg-white/10 hidden md:block" />
              {movie.trailer_key && (
                <a
                  href={`https://www.youtube.com/watch?v=${movie.trailer_key}`}
                  target="_blank"
                  rel="noreferrer"
                  className="h-11 px-5 rounded-lg bg-crimson flex items-center gap-2 font-bold text-sm text-white"
                >
                  ▶ Trailer
                </a>
              )}
              {isAuthenticated && (
                <button
                  onClick={() => watchlistMutation.mutate()}
                  className="h-11 px-[18px] rounded-lg bg-white/[0.09] border border-white/[0.14] flex items-center gap-2 font-bold text-sm text-ink"
                >
                  {movie.in_watchlist ? "✓ In watchlist" : "+ Watchlist"}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="px-8 md:px-12 py-9 flex flex-col gap-2">
        {movie.cast?.length > 0 && (
          <div className="mb-8">
            <div className="font-extrabold text-lg text-ink mb-4">Top billed cast</div>
            <div className="flex gap-4 overflow-x-auto overflow-y-visible py-2.5 no-scrollbar">
              {movie.cast.map((c) => (
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

        <Reviews movieId={movieId} />

        <Rail
          title="More like this"
          subtitle="genre overlap · shared director"
          movies={similar?.items}
          isLoading={!similar}
        />
      </div>
    </div>
  );
}
