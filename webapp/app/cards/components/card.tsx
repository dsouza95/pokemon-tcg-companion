import type { components } from "@/lib/openapi-types";

type CardRead = components["schemas"]["CardRead"];

export function Card({ card }: { card: CardRead }) {
  if (!card.ref_card) return;
  return (
    <div className="group relative flex cursor-pointer flex-col gap-2">
      <div className="bg-muted relative aspect-[2.5/3.5] overflow-hidden rounded-xl transition-transform duration-200 group-hover:scale-105 group-hover:shadow-2xl">
        {/* eslint-disable-next-line @next/next/no-img-element -- image domain is runtime-determined (signed URL), add remotePatterns to next.config.ts to use next/image */}
        <img
          src={card.ref_card.image_url ?? ""}
          alt={card.ref_card.name}
          className="absolute inset-0 h-full w-full object-cover"
        />
      </div>
      <span className="truncate text-center text-sm font-medium">
        {card.ref_card.name}
      </span>
    </div>
  );
}
