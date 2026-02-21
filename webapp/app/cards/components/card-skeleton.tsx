export function CardGridSkeleton() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 gap-4">
      {Array.from({ length: 16 }).map((_, i) => (
        <div key={i} className="flex flex-col gap-2">
          <div className="rounded-xl bg-muted animate-pulse aspect-[2.5/3.5]" />
          <div className="h-4 rounded bg-muted animate-pulse mx-4" />
        </div>
      ))}
    </div>
  );
}
