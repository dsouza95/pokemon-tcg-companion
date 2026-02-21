"use client";

import { Button } from "@/components/ui/button";
import { useCards } from "@/lib/hooks/useCards";
import { useDelayedLoading } from "@/lib/hooks/useDelayedLoading";
import { Add01Icon } from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import { CardGridSkeleton } from "./components/card-skeleton";
import { Card } from "./components/card";

export default function CardsPage() {
  const { data: cards, isLoading, isError } = useCards();
  const showSkeleton = useDelayedLoading(isLoading);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold">My Collection</h1>
          {cards && cards.length > 0 && (
            <span className="text-sm text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
              {cards.length} card{cards.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>
        <Button>
          <HugeiconsIcon icon={Add01Icon} strokeWidth={2} className="w-4 h-4" />
          Add Card
        </Button>
      </div>

      {showSkeleton && <CardGridSkeleton />}

      {isError && (
        <div className="flex flex-col items-center justify-center py-24 gap-2 text-muted-foreground">
          <p className="text-sm">Failed to load your collection.</p>
        </div>
      )}

      {!isLoading && !showSkeleton && !isError && cards && cards.length === 0 && (
        <div className="flex flex-col items-center justify-center py-24 gap-4 text-muted-foreground">
          <p className="text-base">Your collection is empty.</p>
          <Button>
            <HugeiconsIcon icon={Add01Icon} strokeWidth={2} className="w-4 h-4" />
            Add your first card
          </Button>
        </div>
      )}

      {!isLoading && !showSkeleton && !isError && cards && cards.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 gap-4">
          {cards.map((card) => (
            <Card key={card.id} card={card} />
          ))}
        </div>
      )}
    </div>
  );
}
