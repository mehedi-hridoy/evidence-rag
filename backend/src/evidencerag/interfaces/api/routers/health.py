import psycopg
from fastapi import APIRouter, Request
from psycopg_pool import PoolTimeout

from evidencerag.adapters.storage.db import ping
from evidencerag.interfaces.api.errors import ServiceUnavailable

router = APIRouter()


@router.get("/health")
async def health(request: Request) -> dict[str, str]:
    try:
        await ping(request.app.state.pool, request.app.state.settings.db_timeout_s)
    except (PoolTimeout, psycopg.OperationalError) as exc:
        raise ServiceUnavailable("Database is unreachable") from exc
    return {"status": "ok", "database": "ok"}
