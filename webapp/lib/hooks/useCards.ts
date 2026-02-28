"use client";

import { eq, useLiveQuery } from "@tanstack/react-db";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { cardsCollection, refcardsCollection } from "@/lib/db";
import type { components } from "@/lib/openapi-types";

type CardRead = components["schemas"]["CardRead"];

export function useCards() {
  const { data, isLoading, isError } = useLiveQuery(
    (q) =>
      q
        .from({ c: cardsCollection })
        .leftJoin({ rc: refcardsCollection }, ({ c, rc }) =>
          eq(c.ref_card_id, rc.id),
        )
        .orderBy(({ rc }) => rc?.name, "asc")
        .select(({ c, rc }) => ({
          ...c,
          ref_card: rc,
        })),
    [],
  );

  return { data: data || [], isLoading, isError };
}

export function useCreateCard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (file: File) => {
      const urlRes = await fetch("/api/cards/upload-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: file.name, content_type: file.type }),
      });
      if (!urlRes.ok) throw new Error("Failed to get upload URL");
      const { upload_url, image_path } = await urlRes.json();

      const uploadRes = await fetch(upload_url, {
        method: "PUT",
        headers: { "Content-Type": file.type },
        body: file,
      });
      if (!uploadRes.ok) throw new Error("Failed to upload image");

      const cardRes = await fetch("/api/cards/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_path }),
      });
      if (!cardRes.ok) throw new Error("Failed to create card");
      return (await cardRes.json()) as CardRead;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cards"] });
    },
  });
}
