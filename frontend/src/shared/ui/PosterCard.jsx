import { useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { gradientFor } from "../gradient";

const POSTER_BASE = "https://image.tmdb.org/t/p/w342";

export default function PosterCard({ movie, index = 0 }) {
  const [loaded, setLoaded] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: Math.min(index * 0.06, 0.5), ease: "easeOut" }}
      className="flex-none w-[158px]"
    >
      <Link to={`/movie/${movie.id}`} className="group block">
        <div
          className="relative w-[158px] h-[237px] rounded-[10px] overflow-hidden border border-white/[0.08] flex items-end p-3 box-border cursor-pointer transition-transform duration-200 ease-[cubic-bezier(.2,.7,.2,1)] group-hover:-translate-y-2 group-hover:scale-[1.02] group-hover:shadow-[0_22px_46px_-14px_rgba(0,0,0,.9)] group-hover:border-white/25"
          style={{ background: gradientFor(movie.id) }}
        >
          {movie.poster_path && (
            <img
              src={`${POSTER_BASE}${movie.poster_path}`}
              alt={movie.title}
              loading="lazy"
              onLoad={() => setLoaded(true)}
              className="absolute inset-0 w-full h-full object-cover transition-opacity duration-700"
              style={{ opacity: loaded ? 1 : 0 }}
            />
          )}
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/55" style={{ backgroundImage: "linear-gradient(180deg, transparent 45%, rgba(0,0,0,0.55))" }} />
          {movie.rating != null && (
            <div className="absolute top-[9px] right-[9px] inline-flex items-center gap-[3px] bg-black/70 rounded-md px-[7px] py-[3px] font-bold text-[11.5px] text-amber">
              <span className="text-[10px]">★</span>
              {movie.rating.toFixed(1)}
            </div>
          )}
          <div className="relative font-extrabold text-[15px] leading-[1.08] text-white/95 [text-shadow:0_2px_10px_rgba(0,0,0,.7)]">
            {movie.title}
          </div>
        </div>
      </Link>
      <div className="font-mono text-[11px] text-faint mt-2">{movie.year ?? ""}</div>
    </motion.div>
  );
}
