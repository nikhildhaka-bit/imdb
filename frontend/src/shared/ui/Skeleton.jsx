export function PosterSkeleton() {
  return (
    <div className="flex-none w-[158px]">
      <div className="w-[158px] h-[237px] rounded-[10px] bg-surface-2 border border-white/[0.08] animate-pulse" />
      <div className="h-[11px] w-10 bg-surface-2 rounded mt-2 animate-pulse" />
    </div>
  );
}

export function RailSkeleton({ count = 7 }) {
  return (
    <div className="flex gap-4 overflow-hidden py-2.5 px-0.5">
      {Array.from({ length: count }).map((_, i) => (
        <PosterSkeleton key={i} />
      ))}
    </div>
  );
}

export function GridSkeleton({ count = 14 }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-[18px]">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i}>
          <div className="w-full aspect-[2/3] rounded-[10px] bg-surface-2 border border-white/[0.08] animate-pulse" />
          <div className="h-[11px] w-10 bg-surface-2 rounded mt-2 animate-pulse" />
        </div>
      ))}
    </div>
  );
}
