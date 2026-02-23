from typing import Protocol, Sequence, TypeVar
from uuid import UUID

_RRF_K = 60


class HasId(Protocol):
    id: UUID


T = TypeVar("T", bound=HasId)


def reciprocal_rank_fusion(
    ranked_lists: list[Sequence[T]],
    limit: int,
    weights: list[float] | None = None,
) -> list[T]:
    if weights is None:
        weights = [1.0] * len(ranked_lists)

    scores: dict[UUID, float] = {}
    items: dict[UUID, T] = {}

    for weight, ranked_list in zip(weights, ranked_lists, strict=True):
        for rank, item in enumerate(ranked_list, start=1):
            scores[item.id] = scores.get(item.id, 0.0) + weight / (_RRF_K + rank)
            items[item.id] = item

    sorted_ids = sorted(scores, key=lambda id: scores[id], reverse=True)
    return [items[id] for id in sorted_ids[:limit]]
