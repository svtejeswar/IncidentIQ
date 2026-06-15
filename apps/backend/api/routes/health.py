from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from core.config.settings import get_settings
from infrastructure.database.mongodb.client import get_database

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    settings = get_settings()
    return {"status": "ok", "version": settings.app_version}


@router.get("/health/ready")
async def ready() -> JSONResponse:
    checks: dict[str, str] = {}
    all_ok = True

    try:
        db = get_database()
        await db.command("ping")
        checks["mongodb"] = "ok"
    except Exception:
        checks["mongodb"] = "unreachable"
        all_ok = False

    status_code = 200 if all_ok else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if all_ok else "degraded", "checks": checks},
    )
