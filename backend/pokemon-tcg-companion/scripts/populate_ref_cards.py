#!/usr/bin/env python3
"""Populate reference cards from the TCGdex API.

Usage:
    python scripts/populate_ref_cards.py [--help] [set_id]

If set_id is provided, only cards from that set are upserted.
If omitted, all sets are processed.
Cards are upserted using tcg_id as the unique key.
"""

from __future__ import annotations

import argparse
import asyncio

from tcgdexsdk import TCGdex

from cards.application.services import RefCardService
from cards.domain.models import RefCardAdd
from cards.infrastructure.repositories import RefCardRepository
from core.db import AsyncSessionMaker


async def populate_set(tcgdex: TCGdex, set_id: str) -> int:
    """Upsert all cards for a set. Returns number of cards upserted."""
    set_data = await tcgdex.set.get(set_id)
    if not set_data or not set_data.cards:
        print(f"  No cards found for set '{set_id}'")
        return 0

    cards = [
        RefCardAdd(
            tcg_id=card.id,
            tcg_local_id=card.localId,
            name=card.name,
            image_url=card.get_image_url("high", "webp"),
            set_id=set_data.id,
            set_name=set_data.name,
        )
        for card in set_data.cards
    ]

    async with AsyncSessionMaker() as session:
        svc = RefCardService(RefCardRepository(session))
        await svc.upsert_many_cards(cards)

    print(f"  '{set_id}': {len(cards)} upserted")
    return len(cards)


async def main(set_id: str | None = None) -> None:
    tcgdex = TCGdex()

    if set_id:
        sets_to_process = [set_id]
    else:
        all_sets = await tcgdex.set.list()
        sets_to_process = [s.id for s in all_sets]

    print(f"Processing {len(sets_to_process)} set(s)...")

    batch_size = 5
    total_upserted = 0
    for i in range(0, len(sets_to_process), batch_size):
        batch = sets_to_process[i : i + batch_size]
        results = await asyncio.gather(
            *[populate_set(tcgdex, sid) for sid in batch],
            return_exceptions=True,
        )
        for sid, result in zip(batch, results):
            if isinstance(result, BaseException):
                print(f"  '{sid}' failed: {result}")
            else:
                total_upserted += result

    print(f"\nDone: {total_upserted} upserted")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Populate reference cards from the TCGdex API."
    )
    parser.add_argument(
        "set_id", nargs="?", help="Set ID to process (omit to process all sets)"
    )
    args = parser.parse_args()
    asyncio.run(main(args.set_id))
