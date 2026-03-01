"use client";

import { Delete02Icon } from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { useDeleteCard } from "@/lib/hooks/useCards";

export function DeleteCardButton({ cardId }: { cardId: string }) {
  const { mutate: deleteCard, isPending: isDeleting } = useDeleteCard();

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <button
          className="absolute top-1.5 right-1.5 rounded-sm bg-black/40 p-1 opacity-0 backdrop-blur-sm transition-opacity group-hover:opacity-100 hover:bg-black/60"
          disabled={isDeleting}
        >
          <HugeiconsIcon
            icon={Delete02Icon}
            strokeWidth={2}
            className="h-3.5 w-3.5 text-white"
          />
        </button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Remove card</AlertDialogTitle>
          <AlertDialogDescription>
            This will permanently remove the card from your collection.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={() => deleteCard(cardId)}>
            Remove
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
