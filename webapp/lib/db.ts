import { CollectionImpl } from "@tanstack/db";
import { electricCollectionOptions } from "@tanstack/electric-db-collection";

import { components } from "./openapi-types";

const getBaseUrl = () => {
  if (typeof window !== "undefined") {
    return window.location.origin;
  }
  return "";
};

// Initialize the cards collection
export const cardsCollection = new CollectionImpl<
  components["schemas"]["CardRead"]
>({
  ...electricCollectionOptions({
    getKey: (card) => card.id as string,
    shapeOptions: {
      url: `${getBaseUrl()}/api/sync/card`,
    },
  }),
});

// Initialize the refcards collection
export const refcardsCollection = new CollectionImpl<
  components["schemas"]["RefCardRead"]
>({
  ...electricCollectionOptions({
    getKey: (rc) => rc.id as string,
    shapeOptions: {
      url: `${getBaseUrl()}/api/sync/refcard`,
    },
  }),
});
