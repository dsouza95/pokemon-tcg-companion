export function CardGridSkeleton({ count }: { count: number }) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex flex-col gap-2">
          <div className="bg-muted aspect-[2.5/3.5] animate-pulse rounded-sm" />
          <div className="flex h-5 items-center justify-center px-4">
            <div className="bg-muted h-4 w-full animate-pulse rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}
