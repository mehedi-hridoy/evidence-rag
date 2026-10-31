from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from evidencerag.adapters.storage.db import create_pool
from evidencerag.interfaces.api.errors import register_error_handlers
from evidencerag.interfaces.api.routers import health
from evidencerag.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.pool = create_pool(settings.database_url)
        await app.state.pool.open(wait=False)
        yield
        await app.state.pool.close()

    app = FastAPI(title="EvidenceRAG", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    register_error_handlers(app)
    app.include_router(health.router, prefix="/api/v1")
    return app
