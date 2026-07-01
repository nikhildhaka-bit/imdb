import { useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { useAuth } from "./AuthContext";

export default function AuthPage() {
  const [mode, setMode] = useState("login"); // 'login' | 'register'
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");

  const { login, register, isLoggingIn, isRegistering } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from?.pathname ?? "/";

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      if (mode === "login") {
        await login({ email, password });
      } else {
        await register({ email, password, display_name: displayName });
      }
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail ?? "Something went wrong. Please try again.");
    }
  }

  const busy = isLoggingIn || isRegistering;

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center relative">
      <div
        className="absolute inset-0"
        style={{ background: "radial-gradient(circle at 50% 45%,rgba(10,10,13,0.7),rgba(5,5,6,0.96))" }}
      />
      <div className="relative w-full max-w-[400px] bg-surface-2/90 backdrop-blur border border-white/10 rounded-2xl p-9 shadow-[0_30px_70px_-20px_rgba(0,0,0,0.8)] mx-4">
        <div className="font-black text-2xl tracking-[0.02em] text-crimson mb-1">
          <span className="text-[0.72em]">▶</span>
          <span className="text-ink ml-2">MARQUEE</span>
        </div>
        <div className="font-bold text-xl text-ink mb-1.5">{mode === "login" ? "Welcome back" : "Create an account"}</div>
        <div className="text-[13.5px] text-muted mb-6">
          {mode === "login" ? "Sign in to rate films and build your watchlist." : "Join to rate, review, and track what you watch."}
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {mode === "register" && (
            <Field label="Display name">
              <input
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                required
                className="h-11 rounded-lg bg-[#0c0c10] border border-white/[0.12] px-3.5 text-sm text-[#e4e4e8] outline-none focus:border-crimson/50"
              />
            </Field>
          )}
          <Field label="Email">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="h-11 rounded-lg bg-[#0c0c10] border border-white/[0.12] px-3.5 text-sm text-[#e4e4e8] outline-none focus:border-crimson/50"
            />
          </Field>
          <Field label="Password">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="h-11 rounded-lg bg-[#0c0c10] border border-white/[0.12] px-3.5 text-sm text-[#e4e4e8] outline-none focus:border-crimson/50"
            />
          </Field>

          {error && <div className="text-xs text-[#e56]">⚠ {error}</div>}

          <button
            type="submit"
            disabled={busy}
            className="h-[46px] rounded-lg bg-crimson font-bold text-[15px] text-white disabled:opacity-50 mt-1"
          >
            {mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>

        <div className="text-center text-[13.5px] text-muted mt-4">
          {mode === "login" ? (
            <>
              New here?{" "}
              <button onClick={() => setMode("register")} className="text-ink font-semibold underline underline-offset-2">
                Create an account
              </button>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <button onClick={() => setMode("login")} className="text-ink font-semibold underline underline-offset-2">
                Sign in
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <div>
      <div className="font-mono text-[10px] tracking-[0.12em] uppercase text-muted mb-[7px]">{label}</div>
      {children}
    </div>
  );
}
