"use client";

import { Add01Icon } from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useCards, useUploadCard } from "@/lib/hooks/useCards";
import { useDelayedLoading } from "@/lib/hooks/useDelayedLoading";

import { Card } from "./components/card";
import { CardGridSkeleton } from "./components/card-skeleton";
import { UploadCardDialog } from "./components/upload-card-dialog";

export default function CardsPage() {
  const { data: cards, isLoading, isError } = useCards();
  const showSkeleton = useDelayedLoading(isLoading);
  const [dialogOpen, setDialogOpen] = useState(false);
  const { mutateAsync: uploadCard } = useUploadCard();

  return (
    <>
      <UploadCardDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onUpload={uploadCard}
      />
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">My Collection</h1>
            {cards && cards.length > 0 && (
              <span className="text-muted-foreground bg-muted rounded-full px-2 py-0.5 text-sm">
                {cards.length} card{cards.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>
          <Button onClick={() => setDialogOpen(true)}>
            <HugeiconsIcon
              icon={Add01Icon}
              strokeWidth={2}
              className="h-4 w-4"
            />
            Add Card
          </Button>
        </div>

        {showSkeleton && <CardGridSkeleton />}

        {isError && (
          <div className="text-muted-foreground flex flex-col items-center justify-center gap-2 py-24">
            <p className="text-sm">Failed to load your collection.</p>
          </div>
        )}

        {!isLoading &&
          !showSkeleton &&
          !isError &&
          cards &&
          cards.length === 0 && (
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

        {!isLoading &&
          !showSkeleton &&
          !isError &&
          cards &&
          cards.length > 0 && (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8">
              {cards.map((card) => (
                <Card key={card.id} card={card} />
              ))}
            </div>
          )}
      </div>
    </>
  );
}
