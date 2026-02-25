"use client";

import dynamic from "next/dynamic";

import { CardGridSkeleton } from "./components/card-skeleton";

const CardsView = dynamic(
  () => import("./components/cards-view").then((mod) => mod.CardsView),
  {
    ssr: false,
    loading: () => <CardGridSkeleton />,
  },
);

export default function CardsPage() {
  return <CardsView />;
}
