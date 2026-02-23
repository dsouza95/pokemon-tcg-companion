from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cards.interface.api import router as cards_router
from core.auth import require_auth
from core.logfire import setup_logfire
from core.settings import settings
from lifespan import lifespan

app = FastAPI(title="Pokémon TCG Companion", lifespan=lifespan)
setup_logfire(fastapi_app=app)

allowed_origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cards_router)


@app.get("/", dependencies=[Depends(require_auth)])
async def root():
    return {"message": "Pokémon TCG Companion"}
