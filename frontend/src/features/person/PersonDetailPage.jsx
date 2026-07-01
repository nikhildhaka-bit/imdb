import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../shared/api";
import { gradientFor } from "../../shared/gradient";

const PROFILE_BASE = "https://image.tmdb.org/t/p/w342";
const THUMB_BASE = "https://image.tmdb.org/t/p/w92";

export default function PersonDetailPage() {
  const { id } = useParams();
  const personId = Number(id);

  const { data: person, isLoading } = useQuery({
    queryKey: ["person", personId],
    queryFn: () => api.get(`/people/${personId}`).then((r) => r.data),
  });

  if (isLoading || !person) {
    return <div className="h-[400px] bg-surface-2 animate-pulse" />;
  }

  return (
    <div className="px-8 md:px-12 py-11 flex flex-col">
      <div className="flex flex-col md:flex-row gap-10 pb-9">
        <div
          className="w-[240px] h-[300px] flex-none rounded-2xl border border-white/10 overflow-hidden"
          style={{ background: gradientFor(person.id) }}
        >
          {person.profile_path && (
            <img src={`${PROFILE_BASE}${person.profile_path}`} alt={person.name} className="w-full h-full object-cover" />
          )}
        </div>
        <div className="flex-1 pt-1.5">
          {person.known_for_department && (
            <div className="font-mono text-[11px] tracking-[0.2em] uppercase text-crimson font-semibold mb-3">
              {person.known_for_department}
            </div>
          )}
          <div className="font-black text-[42px] leading-none tracking-tight text-white">{person.name}</div>
          <div className="flex gap-7 my-5">
            <Stat label="Credits" value={person.credits_count} />
            {person.avg_rating != null && <Stat label="Avg rating" value={person.avg_rating} color="text-amber" />}
            {person.birthday && <Stat label="Born" value={person.birthday.slice(0, 4)} />}
          </div>
          {person.bio && <div className="text-[15px] leading-[1.62] text-[#b4b4be] max-w-[720px]">{person.bio}</div>}
        </div>
      </div>

      <div className="flex items-baseline gap-3 mb-4">
        <span className="font-extrabold text-lg text-ink">Filmography</span>
        <span className="font-mono text-[11px] text-faint">sorted by year</span>
      </div>
      <div className="flex flex-col gap-0.5">
        {person.filmography.map((f) => (
          <Link
            key={f.movie_id}
            to={`/movie/${f.movie_id}`}
            className="flex items-center gap-[18px] px-3.5 py-3 rounded-xl bg-surface-2 border border-white/5 hover:border-white/10"
          >
            <div
              className="w-[46px] h-[69px] rounded-md flex-none border border-white/[0.08] overflow-hidden"
              style={{ background: gradientFor(f.movie_id) }}
            >
              {f.poster_path && <img src={`${THUMB_BASE}${f.poster_path}`} alt="" className="w-full h-full object-cover" />}
            </div>
            <div className="w-14 font-mono text-[13px] text-muted flex-none">{f.year ?? ""}</div>
            <div className="flex-1 font-bold text-[16px] text-ink">{f.title}</div>
            <div className="text-[13.5px] text-muted">{f.role}</div>
            {f.rating != null && (
              <div className="inline-flex items-center gap-1 font-bold text-[13.5px] text-amber w-14 justify-end">
                ★ {f.rating.toFixed(1)}
              </div>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}

function Stat({ label, value, color = "text-ink" }) {
  return (
    <div>
      <div className={`font-extrabold text-[22px] ${color}`}>{value}</div>
      <div className="font-mono text-[10.5px] tracking-[0.1em] uppercase text-faint mt-0.5">{label}</div>
    </div>
  );
}
