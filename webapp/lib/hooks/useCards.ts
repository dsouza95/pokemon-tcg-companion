import type { components } from "@/lib/openapi-types";
import { useQuery } from "@tanstack/react-query";

type Card = components["schemas"]["Card"];

export function useCards() {
  return useQuery<Card[], Error>({
    queryKey: ["cards"],
    queryFn: async () => {
      const res = await fetch("/api/cards");
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
