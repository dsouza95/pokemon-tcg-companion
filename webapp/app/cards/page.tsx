"use client";

import { Add01Icon } from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import dynamic from "next/dynamic";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useCreateCard } from "@/lib/hooks/useCards";

import { CardGridSkeleton } from "./components/card-skeleton";
import { UploadCardDialog } from "./components/upload-card-dialog";

const NUM_SKELETON_CARDS = 10;
const CardsView = dynamic(
  () => import("./components/cards-view").then((mod) => mod.CardsView),
  {
    ssr: false,
    loading: () => <CardGridSkeleton count={NUM_SKELETON_CARDS} />,
  },
);

export default function CardsPage() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { mutateAsync: uploadCard } = useCreateCard();

  return (
    <div className="flex flex-col gap-6">
      <UploadCardDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onUpload={uploadCard}
      />
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">My Collection</h1>
        <Button onClick={() => setDialogOpen(true)}>
          <HugeiconsIcon icon={Add01Icon} strokeWidth={2} className="h-4 w-4" />
          Add Card
        </Button>
      </div>
      <CardsView
        numSkeletonCards={NUM_SKELETON_CARDS}
        onAddCard={() => setDialogOpen(true)}
      />
    </div>
  );
}
