from fastapi import APIRouter

from .cards import router as cards_router
from .sync import router as sync_router
from .webhooks import router as webhooks_router

router = APIRouter()
router.include_router(cards_router)
router.include_router(webhooks_router)
router.include_router(sync_router)
