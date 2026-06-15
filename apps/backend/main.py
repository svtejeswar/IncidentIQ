from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import assistant, documents, health, search, stats
from core.config.settings import get_settings
from core.logging.logger import configure_logging, get_logger
from infrastructure.database.mongodb.client import connect, disconnect

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(debug=settings.debug)
    log.info("incidentiq_starting", env=settings.app_env, version=settings.app_version)

    try:
        await connect(settings.mongodb_uri, settings.mongodb_database)
    except Exception as exc:
        if settings.is_production:
            raise
        log.warning("mongodb_connect_failed", error=str(exc), note="server running in degraded mode — database calls will fail")

    yield

    await disconnect()
    log.info("incidentiq_stopped")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="IncidentIQ API",
        description="AI-powered incident intelligence platform",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(documents.router, prefix="/api/v1")
    app.include_router(search.router, prefix="/api/v1")
    app.include_router(assistant.router, prefix="/api/v1")
    app.include_router(stats.router, prefix="/api/v1")

    return app


app = create_app()
