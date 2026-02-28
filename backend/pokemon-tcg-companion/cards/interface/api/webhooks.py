from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from cards.domain.models.card import Card
from cards.infrastructure.flows.match_card import FLOW_NAME
from core import flows
from core.auth import verify_pubsub_token
from core.pubsub_model import PubSubEnvelope

router = APIRouter(prefix="/cards/webhooks", tags=["webhooks"])


@router.post("/card-created", dependencies=[Depends(verify_pubsub_token)])
async def handle_card_created(envelope: PubSubEnvelope):
    try:
        payload = envelope.get_payload(Card)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors()) from e

    await flows.arun_deployment(
        name=flows.get_deployment_name(FLOW_NAME),
        parameters={"card_id": str(payload.id), "image_path": payload.image_path},
        timeout=0,
    )

    return {"status": "success", "card_id": payload.id}
