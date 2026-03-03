import { CollectionImpl } from "@tanstack/db";
import { electricCollectionOptions } from "@tanstack/electric-db-collection";

import { components } from "./openapi-types";

const getBaseUrl = () => {
  if (typeof window !== "undefined") {
    return window.location.origin;
  }
  return "";
};

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

export const tcgSetsCollection = new CollectionImpl<
  components["schemas"]["TcgSetRead"]
>({
  ...electricCollectionOptions({
    getKey: (s) => s.id,
    shapeOptions: {
      url: `${getBaseUrl()}/api/sync/tcgset`,
    },
  }),
});
