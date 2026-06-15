from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING
from core.logging.logger import get_logger

log = get_logger(__name__)

_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect(mongodb_uri: str, database_name: str) -> None:
    global _client, _database
    _client = AsyncIOMotorClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    _database = _client[database_name]
    await _client.admin.command("ping")
    await _ensure_indexes(_database)
    log.info("mongodb_connected", database=database_name)


async def disconnect() -> None:
    global _client, _database
    if _client:
        _client.close()
        _client = None
        _database = None
    log.info("mongodb_disconnected")


def get_database() -> AsyncIOMotorDatabase:
    if _database is None:
        raise RuntimeError("MongoDB not connected. Call connect() first.")
    return _database


async def _ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    await db["documents"].create_indexes([
        IndexModel([("status", ASCENDING)]),
        IndexModel([("document_type", ASCENDING)]),
        IndexModel([("created_at", ASCENDING)]),
    ])

    await db["chunks"].create_indexes([
        IndexModel([("document_id", ASCENDING)]),
        IndexModel([("document_type", ASCENDING)]),
    ])

    await db["incidents"].create_indexes([
        IndexModel([("document_id", ASCENDING)]),
        IndexModel([("severity", ASCENDING)]),
    ])

    log.info("mongodb_indexes_ensured")
