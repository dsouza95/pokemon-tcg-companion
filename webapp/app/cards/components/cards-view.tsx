"use client";

import { Add01Icon } from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import { useCallback, useState } from "react";

import { Button } from "@/components/ui/button";
import { useCards, useCreateCard } from "@/lib/hooks/useCards";
import { cn } from "@/lib/utils";

import { Card } from "./card";
import { CardGridSkeleton } from "./card-skeleton";
import { UploadCardDialog } from "./upload-card-dialog";

export function CardsView({ numSkeletonCards }: { numSkeletonCards: number }) {
  const { data: cards = [], isLoading, isError } = useCards();
  const [dialogOpen, setDialogOpen] = useState(false);
  const { mutateAsync: uploadCard } = useCreateCard();
  const [loadedImages, setLoadedImages] = useState<Set<string>>(new Set());

  const handleImageLoad = useCallback((id: string) => {
    setLoadedImages((prev) => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
  }, []);

  const requiredLoadCount = Math.min(cards.length, numSkeletonCards);
  const isReady =
    !isLoading &&
    (cards.length === 0 || loadedImages.size >= requiredLoadCount);

  return (
    <>
      <UploadCardDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onUpload={uploadCard}
      />

      {!isReady && !isError && <CardGridSkeleton count={numSkeletonCards} />}

      <div
        className={cn(
          "flex flex-col gap-6",
          !isReady && !isError
            ? "hidden"
            : "animate-in fade-in zoom-in-[0.98] duration-200",
        )}
      >
        {isError && (
          <div className="text-muted-foreground flex flex-col items-center justify-center gap-2 py-24">
            <p className="text-sm">Failed to load your collection.</p>
          </div>
        )}

        {!isError && cards && cards.length === 0 && (
          <div className="text-muted-foreground flex flex-col items-center justify-center gap-4 py-24">
            <p className="text-base">Your collection is empty.</p>
            <Button onClick={() => setDialogOpen(true)}>
              <HugeiconsIcon
                icon={Add01Icon}
                strokeWidth={2}
                className="h-4 w-4"
              />
              Add your first card
            </Button>
          </div>
        )}

        {!isError && cards && cards.length > 0 && (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8">
            {cards.map((card) => (
              <Card
                key={card.id}
                card={card}
                onImageLoad={() => handleImageLoad(card.id)}
              />
            ))}
          </div>
        )}
      </div>
    </>
  );
}
