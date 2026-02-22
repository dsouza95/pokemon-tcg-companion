import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { components } from "@/lib/openapi-types";

type Card = components["schemas"]["Card"];

export function useCards() {
  return useQuery<Card[], Error>({
    queryKey: ["cards"],
    queryFn: async () => {
      const res = await fetch("/api/cards/");
      if (!res.ok) throw new Error("Failed to fetch cards");
      return (await res.json()) as Card[];
    },
  });
}

export function useCard(id: string) {
  return useQuery<Card, Error>({
    queryKey: ["card", id],
    queryFn: async () => {
      const res = await fetch(`/api/cards/${id}`);
      if (!res.ok) throw new Error("Failed to fetch card");
      return (await res.json()) as Card;
    },
  });
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
      return (await cardRes.json()) as Card;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cards"] });
    },
  });
}
