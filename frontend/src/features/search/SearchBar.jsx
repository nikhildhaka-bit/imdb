import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../shared/api";
import { gradientFor } from "../../shared/gradient";

const THUMB_BASE = "https://image.tmdb.org/t/p/w92";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const [debounced, setDebounced] = useState("");
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const containerRef = useRef(null);

  useEffect(() => {
    const t = setTimeout(() => setDebounced(query.trim()), 400);
    return () => clearTimeout(t);
  }, [query]);

  useEffect(() => {
    function onClickOutside(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const { data, isFetching } = useQuery({
    queryKey: ["search-typeahead", debounced],
    queryFn: () => api.get("/search", { params: { q: debounced } }).then((r) => r.data),
    enabled: debounced.length > 0,
    staleTime: 30_000,
  });

  const suggestions = (data?.items ?? []).slice(0, 4);

  function submit() {
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
      setOpen(false);
    }
  }

  function goTo(item) {
    setOpen(false);
    navigate(item.media_type === "person" ? `/person/${item.id}` : `/movie/${item.id}`);
  }

  return (
    <div ref={containerRef} className="relative w-full max-w-[380px]">
      <div
        className={`h-[38px] rounded-full bg-surface-2 border flex items-center gap-2.5 px-4 ${
          open ? "border-crimson/60 rounded-b-none" : "border-white/[0.09]"
        }`}
      >
        <span className="text-faint text-sm">⌕</span>
        <input
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="Search movies, shows, people…"
          className="bg-transparent outline-none text-[13.5px] text-ink placeholder:text-faint w-full"
        />
      </div>

      {open && debounced.length > 0 && (
        <div className="absolute top-full left-0 w-full bg-surface-2 border border-t-0 border-crimson/40 rounded-b-xl shadow-[0_30px_60px_-20px_rgba(0,0,0,0.9)] z-30 overflow-hidden">
          <div className="px-4 pt-[9px] pb-1.5 font-mono text-[10px] tracking-[0.14em] uppercase text-faint">
            Suggestions
          </div>
          {suggestions.map((item) => (
            <button
              key={`${item.media_type}-${item.id}`}
              onClick={() => goTo(item)}
              className="w-full flex items-center gap-[11px] px-3.5 py-2 hover:bg-white/[0.04] text-left"
            >
              <div
                className="w-[34px] h-[50px] flex-none border border-white/[0.08] overflow-hidden bg-cover bg-center"
                style={{
                  background: gradientFor(item.id),
                  borderRadius: item.media_type === "person" ? "999px" : "5px",
                }}
              >
                {item.poster_path && (
                  <img src={`${THUMB_BASE}${item.poster_path}`} alt="" className="w-full h-full object-cover" />
                )}
              </div>
              <div className="min-w-0">
                <div className="font-semibold text-[13.5px] text-ink truncate">{item.title}</div>
                <div className="font-mono text-[10.5px] text-faint mt-0.5">{item.meta}</div>
              </div>
            </button>
          ))}
          <div className="border-t border-white/[0.06] px-4 py-[13px] flex items-center gap-2.5">
            {isFetching ? (
              <>
                <span className="w-[15px] h-[15px] rounded-full border-2 border-white/15 border-t-crimson animate-spin" />
                <span className="font-mono text-[11px] text-muted">Searching…</span>
              </>
            ) : (
              <button onClick={submit} className="font-mono text-[11px] text-muted hover:text-ink">
                Press Enter for all results →
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
