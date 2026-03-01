"use client";

import Image from "next/image";
import { useState } from "react";

import type { components } from "@/lib/openapi-types";
import { cn } from "@/lib/utils";

import { CardSkeleton } from "./card-skeleton";
import { DeleteCardButton } from "./delete-card-button";

type CardRead = components["schemas"]["CardRead"];

export function Card({
  card,
  onImageLoad,
}: {
  card: CardRead;
  onImageLoad?: () => void;
}) {
  const [imageLoaded, setImageLoaded] = useState(false);

  if (!card.ref_card) {
    return <CardSkeleton />;
  }

  return (
    <div className="group relative flex cursor-pointer flex-col gap-2">
      <div
        className={cn(
          "bg-muted relative aspect-[2.5/3.5] overflow-hidden rounded-sm transition-transform duration-200 group-hover:scale-105 group-hover:shadow-2xl",
          !imageLoaded && "animate-pulse",
        )}
      >
        <DeleteCardButton cardId={card.id} />
        {card.ref_card.image_url && (
          <Image
            src={card.ref_card.image_url}
            alt={card.ref_card.name}
            fill
            sizes="(max-width: 640px) 50vw, (max-width: 768px) 33vw, (max-width: 1024px) 25vw, (max-width: 1280px) 20vw, 16vw"
            priority={true}
            className={cn(
              "object-cover transition-opacity duration-300",
              imageLoaded ? "opacity-100" : "opacity-0",
            )}
            onLoad={() => {
              setImageLoaded(true);
              onImageLoad?.();
            }}
          />
        )}
      </div>
      <span className="truncate text-center text-sm font-medium">
        {card.ref_card.name}
      </span>
    </div>
  );
}
