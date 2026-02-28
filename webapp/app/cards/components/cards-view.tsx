"use client";

import { Add01Icon } from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";

import { Button } from "@/components/ui/button";
import { useCards } from "@/lib/hooks/useCards";

import { Card } from "./card";
import { CardGridSkeleton } from "./card-skeleton";

export function CardsView({
  numSkeletonCards,
  onAddCard,
}: {
  numSkeletonCards: number;
  onAddCard: () => void;
}) {
  const { data: cards = [], isLoading, isError } = useCards();

  if (isLoading) return <CardGridSkeleton count={numSkeletonCards} />;

  if (isError)
    return (
      <div className="text-muted-foreground flex flex-col items-center justify-center gap-2 py-24">
        <p className="text-sm">Failed to load your collection.</p>
      </div>
    );

  if (cards.length === 0)
    return (
      <div className="text-muted-foreground flex flex-col items-center justify-center gap-4 py-24">
        <p className="text-base">Your collection is empty.</p>
        <Button onClick={onAddCard}>
          <HugeiconsIcon icon={Add01Icon} strokeWidth={2} className="h-4 w-4" />
          Add your first card
        </Button>
      </div>
    );

  return (
    <div className="animate-in fade-in zoom-in-[0.98] flex flex-col gap-6 duration-200">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8">
        {cards.map((card) => (
          <Card key={card.id} card={card} />
        ))}
      </div>
    </div>
  );
}
