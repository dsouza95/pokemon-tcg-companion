"use client";

import dynamic from "next/dynamic";

import { CardGridSkeleton } from "./components/card-skeleton";
const NUM_SKELETON_CARDS = 10;
const CardsView = dynamic(
  () => import("./components/cards-view").then((mod) => mod.CardsView),
  {
    ssr: false,
    loading: () => <CardGridSkeleton count={NUM_SKELETON_CARDS} />,
  },
);

export default function CardsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold">My Collection</h1>
        </div>
      </div>
      <CardsView numSkeletonCards={NUM_SKELETON_CARDS} />
    </div>
  );
}
