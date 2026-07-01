import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../shared/api";
import { gradientFor } from "../../shared/gradient";
import { GridSkeleton } from "../../shared/ui/Skeleton";

const POSTER_BASE = "https://image.tmdb.org/t/p/w342";

export default function WatchlistPage() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["watchlist"],
    queryFn: () => api.get("/me/watchlist").then((r) => r.data),
  });

  const removeMutation = useMutation({
    mutationFn: (movieId) => api.delete(`/me/watchlist/${movieId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["watchlist"] }),
  });

  return (
    <div className="px-8 md:px-12 py-10 flex flex-col gap-6">
      <div className="flex items-baseline gap-3.5">
        <span className="font-black text-3xl text-ink tracking-tight">My watchlist</span>
        {data && <span className="font-mono text-xs text-faint">{data.total} to watch</span>}
      </div>

      {isLoading ? (
        <GridSkeleton count={12} />
      ) : data.items.length === 0 ? (
        <div className="py-20 text-center flex flex-col items-center gap-3">
          <div className="text-muted text-sm">Your watchlist is empty.</div>
          <Link to="/movies" className="h-10 px-5 rounded-lg bg-crimson flex items-center font-bold text-sm text-white">
            Browse movies
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-[22px]">
          {data.items.map((movie) => (
            <div key={movie.id} className="group">
              <div
                className="relative w-full aspect-[2/3] rounded-xl overflow-hidden border border-white/[0.08] transition-transform duration-200 group-hover:-translate-y-2 group-hover:scale-[1.02]"
                style={{ background: gradientFor(movie.id) }}
              >
                <Link to={`/movie/${movie.id}`}>
                  {movie.poster_path && (
                    <img src={`${POSTER_BASE}${movie.poster_path}`} alt={movie.title} className="absolute inset-0 w-full h-full object-cover" />
                  )}
                  <div className="absolute inset-0" style={{ backgroundImage: "linear-gradient(180deg, transparent 42%, rgba(0,0,0,0.6))" }} />
                  {movie.rating != null && (
                    <div className="absolute top-2.5 left-2.5 inline-flex items-center gap-[3px] bg-black/70 rounded-md px-[7px] py-[3px] font-bold text-[11px] text-amber">
                      ★ {movie.rating.toFixed(1)}
                    </div>
                  )}
                  <div className="absolute inset-x-3 bottom-3 font-extrabold text-[15px] leading-tight text-white/95 [text-shadow:0_2px_10px_rgba(0,0,0,.7)]">
                    {movie.title}
                  </div>
                </Link>
                <button
                  onClick={() => removeMutation.mutate(movie.id)}
                  className="absolute top-2.5 right-2.5 w-7 h-7 rounded-full bg-black/70 border border-white/[0.14] flex items-center justify-center text-ink text-sm"
                  title="Remove from watchlist"
                >
                  ×
                </button>
              </div>
              <div className="font-mono text-[11px] text-faint mt-2.5">{movie.year}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
