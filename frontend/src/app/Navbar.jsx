import { useState, useRef, useEffect } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/AuthContext";
import SearchBar from "../features/search/SearchBar";

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const menuRef = useRef(null);

  useEffect(() => {
    function onClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  return (
    <div className="sticky top-0 z-40 h-16 flex items-center gap-[34px] px-8 border-b border-white/[0.07] bg-surface/95 backdrop-blur">
      <Link to="/" className="font-black text-[21px] tracking-[0.02em] text-crimson flex items-center flex-none">
        <span className="text-[0.72em]">▶</span>
        <span className="text-ink ml-2">MARQUEE</span>
      </Link>

      <div className="hidden md:flex gap-[26px] font-semibold text-sm flex-none">
        <NavLink to="/" end className={({ isActive }) => (isActive ? "text-ink" : "text-muted hover:text-ink")}>
          Home
        </NavLink>
        <NavLink
          to="/movies"
          className={({ isActive }) => (isActive ? "text-ink" : "text-muted hover:text-ink")}
        >
          Movies
        </NavLink>
      </div>

      <div className="flex-1 flex justify-center">
        <SearchBar />
      </div>

      {isAuthenticated ? (
        <div ref={menuRef} className="relative flex-none">
          <button
            onClick={() => setMenuOpen((v) => !v)}
            className="w-[34px] h-[34px] rounded-full flex items-center justify-center font-bold text-[13px] text-white"
            style={{ background: "linear-gradient(140deg,#3a2452,#e11d2e)" }}
          >
            {user.display_name?.[0]?.toUpperCase() ?? "?"}
          </button>
          {menuOpen && (
            <div className="absolute right-0 top-11 w-44 bg-surface-2 border border-white/10 rounded-xl overflow-hidden shadow-[0_20px_50px_-12px_rgba(0,0,0,0.8)]">
              <Link
                to="/profile"
                onClick={() => setMenuOpen(false)}
                className="block px-4 py-3 text-sm text-ink hover:bg-white/5"
              >
                Profile
              </Link>
              <Link
                to="/watchlist"
                onClick={() => setMenuOpen(false)}
                className="block px-4 py-3 text-sm text-ink hover:bg-white/5"
              >
                Watchlist
              </Link>
              <button
                onClick={async () => {
                  setMenuOpen(false);
                  await logout();
                  navigate("/");
                }}
                className="w-full text-left px-4 py-3 text-sm text-muted hover:bg-white/5"
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      ) : (
        <Link
          to="/login"
          className="flex-none h-9 px-4 rounded-lg bg-crimson flex items-center font-bold text-sm text-white"
        >
          Sign in
        </Link>
      )}
    </div>
  );
}
