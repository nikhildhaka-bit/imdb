import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../../shared/api";
import { useAuth } from "../auth/AuthContext";
import Rail from "../../shared/ui/Rail";

const BACKDROP_BASE = "https://image.tmdb.org/t/p/original";

function useFeed(feed) {
  return useQuery({
    queryKey: ["feed", feed],
    queryFn: () => api.get("/movies", { params: { feed } }).then((r) => r.data),
    staleTime: 5 * 60_000,
  });
}

function Hero({ movieId }) {
  const { data: movie } = useQuery({
    queryKey: ["movie", movieId],
    queryFn: () => api.get(`/movies/${movieId}`).then((r) => r.data),
    enabled: Boolean(movieId),
    staleTime: 5 * 60_000,
  });

  if (!movie) {
    return <div className="h-[440px] bg-surface-2 animate-pulse" />;
  }

  return (
    <div
      className="relative h-[440px] flex items-end p-11 bg-cover bg-center"
      style={movie.backdrop_path ? { backgroundImage: `url(${BACKDROP_BASE}${movie.backdrop_path})` } : undefined}
    >
      <div
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(90deg,rgba(10,10,13,0.94) 0%,rgba(10,10,13,0.7) 34%,rgba(10,10,13,0.15) 70%,transparent 100%),linear-gradient(0deg,#0a0a0d 2%,transparent 40%)",
        }}
      />
      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative max-w-[560px]"
      >
        <div className="font-mono text-[11px] tracking-[0.22em] uppercase text-crimson font-semibold mb-3.5">
          Featured today
        </div>
        <div className="font-black text-[52px] leading-[0.98] tracking-tight text-white mb-4">{movie.title}</div>
        <div className="flex items-center gap-3.5 mb-4 text-sm text-[#c8c8d0] font-semibold">
          {movie.vote_average != null && (
            <span className="inline-flex items-center gap-[5px] text-amber">
              <span>★</span>
              {movie.vote_average.toFixed(1)}
            </span>
          )}
          {movie.release_date && <span>{movie.release_date.slice(0, 4)}</span>}
          {movie.runtime && (
            <span>
              {Math.floor(movie.runtime / 60)}h {movie.runtime % 60}m
            </span>
          )}
          {movie.genres?.length > 0 && <span>{movie.genres.map((g) => g.name).join(" · ")}</span>}
        </div>
        {movie.overview && (
          <div className="text-[15px] leading-[1.55] text-[#b4b4be] mb-6 line-clamp-3">{movie.overview}</div>
        )}
        <div className="flex gap-3">
          <Link
            to={`/movie/${movie.id}`}
            className="h-[46px] px-6 rounded-lg bg-crimson flex items-center gap-2 font-bold text-[15px] text-white"
          >
            ▶ View details
          </Link>
        </div>
      </motion.div>
    </div>
  );
}

export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const trending = useFeed("trending");
  const topRated = useFeed("top_rated");
  const forYou = useQuery({
    queryKey: ["for-you", isAuthenticated],
    queryFn: () =>
      isAuthenticated
        ? api.get("/me/feed").then((r) => r.data)
        : api.get("/movies", { params: { feed: "trending" } }).then((r) => r.data),
    staleTime: 5 * 60_000,
  });

  const heroId = trending.data?.items?.[0]?.id;

  return (
    <div className="flex flex-col gap-8">
      <Hero movieId={heroId} />
      <div className="px-8 md:px-12 pb-14 flex flex-col gap-8">
        <Rail
          title="For you"
          subtitle={isAuthenticated ? "based on your top genres" : "sign in to personalize this"}
          movies={forYou.data?.items}
          isLoading={forYou.isLoading}
        />
        <Rail title="Trending this week" movies={trending.data?.items} isLoading={trending.isLoading} />
        <Rail title="Top rated" movies={topRated.data?.items} isLoading={topRated.isLoading} />
      </div>
    </div>
  );
}
