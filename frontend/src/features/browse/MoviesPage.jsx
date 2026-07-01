import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../shared/api";
import { GENRES } from "../../shared/genres";
import PosterCard from "../../shared/ui/PosterCard";
import { GridSkeleton } from "../../shared/ui/Skeleton";

export default function MoviesPage() {
  const [genre, setGenre] = useState("");
  const [minRating, setMinRating] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ["browse", genre, minRating, page],
    queryFn: () =>
      api
        .get("/movies", {
          params: {
            page,
            ...(genre && { genre }),
            ...(minRating && { min_rating: minRating }),
          },
        })
        .then((r) => r.data),
    staleTime: 60_000,
  });

  return (
    <div className="px-8 md:px-12 py-8 flex flex-col gap-6">
      <div className="flex items-baseline gap-3.5 flex-wrap">
        <span className="font-black text-3xl text-ink tracking-tight">Movies</span>
        <div className="flex-1" />
        <select
          value={genre}
          onChange={(e) => {
            setGenre(e.target.value);
            setPage(1);
          }}
          className="h-9 px-3 rounded-lg bg-surface-2 border border-white/10 text-sm text-muted"
        >
          <option value="">All genres</option>
          {GENRES.map((g) => (
            <option key={g.id} value={g.id}>
              {g.name}
            </option>
          ))}
        </select>
        <select
          value={minRating}
          onChange={(e) => {
            setMinRating(e.target.value);
            setPage(1);
          }}
          className="h-9 px-3 rounded-lg bg-surface-2 border border-white/10 text-sm text-muted"
        >
          <option value="">Any rating</option>
          <option value="9">9+</option>
          <option value="8">8+</option>
          <option value="7">7+</option>
          <option value="6">6+</option>
        </select>
      </div>

      {isLoading ? (
        <GridSkeleton />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-[18px]">
          {data.items.map((movie, i) => (
            <PosterCard key={movie.id} movie={movie} index={i % 14} />
          ))}
        </div>
      )}

      <div className="flex items-center justify-center gap-4 mt-4">
        <button
          disabled={page <= 1}
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          className="h-9 px-4 rounded-lg bg-surface-2 border border-white/10 text-sm text-muted disabled:opacity-40"
        >
          Previous
        </button>
        <span className="font-mono text-xs text-faint">Page {page}</span>
        <button
          disabled={isFetching}
          onClick={() => setPage((p) => p + 1)}
          className="h-9 px-4 rounded-lg bg-surface-2 border border-white/10 text-sm text-muted disabled:opacity-40"
        >
          Next
        </button>
      </div>
    </div>
  );
}
