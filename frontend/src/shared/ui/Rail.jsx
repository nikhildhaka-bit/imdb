import PosterCard from "./PosterCard";
import { RailSkeleton } from "./Skeleton";

export default function Rail({ title, subtitle, movies, isLoading }) {
  if (!isLoading && (!movies || movies.length === 0)) return null;

  return (
    <div>
      <div className="flex items-baseline gap-3 mb-4">
        <span className="font-extrabold text-xl text-ink">{title}</span>
        {subtitle && <span className="font-mono text-[11px] text-faint">{subtitle}</span>}
      </div>
      {isLoading ? (
        <RailSkeleton />
      ) : (
        <div className="flex gap-4 overflow-x-auto overflow-y-visible py-2.5 px-0.5 no-scrollbar">
          {movies.map((movie, i) => (
            <PosterCard key={movie.id} movie={movie} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
