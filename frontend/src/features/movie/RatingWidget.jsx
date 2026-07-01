import { useState } from "react";

export default function RatingWidget({ value, onRate, onClear }) {
  const [hover, setHover] = useState(null);
  const active = hover ?? value ?? 0;

  return (
    <div className="flex flex-col gap-[7px]">
      <span className="font-mono text-[10px] tracking-[0.14em] uppercase text-faint">Your rating</span>
      <div className="flex gap-1">
        {Array.from({ length: 10 }, (_, i) => i + 1).map((n) => {
          const on = n <= active;
          return (
            <button
              key={n}
              onMouseEnter={() => setHover(n)}
              onMouseLeave={() => setHover(null)}
              onClick={() => (value === n ? onClear() : onRate(n))}
              className="w-[26px] h-[30px] rounded-md flex items-center justify-center font-bold text-xs transition-colors"
              style={{
                background: on ? "rgba(245,197,24,0.16)" : "#141419",
                border: `1px solid ${on ? "rgba(245,197,24,0.45)" : "rgba(255,255,255,0.1)"}`,
                color: on ? "#f5c518" : "#6a6a76",
              }}
              title={value === n ? "Click to remove your rating" : `Rate ${n}`}
            >
              {n}
            </button>
          );
        })}
      </div>
    </div>
  );
}
