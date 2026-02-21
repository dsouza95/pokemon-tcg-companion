import type { components } from "@/lib/openapi-types";

type Card = components["schemas"]["Card"];

export function Card({ card }: { card: Card }) {
  return (
    <div className="group relative flex flex-col gap-2 cursor-pointer">
      <div className="relative overflow-hidden rounded-xl bg-muted aspect-[2.5/3.5] transition-transform duration-200 group-hover:scale-105 group-hover:shadow-2xl">
          <img
            src={card.image_url}
            alt={card.name}
            className="absolute inset-0 w-full h-full object-cover"
          />
      </div>
      <span className="text-sm font-medium truncate text-center">{card.name}</span>
    </div>
  );
}
