from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter

from infrastructure.database.mongodb.client import get_database

router = APIRouter(prefix="/stats", tags=["stats"])

INCIDENT_TYPES = ["incident_report", "rca", "postmortem"]


@router.get("")
async def get_platform_stats() -> dict:
    db = get_database()
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    documents_indexed = await db.documents.count_documents({"status": "completed"})
    docs_this_week = await db.documents.count_documents(
        {"status": "completed", "created_at": {"$gte": week_ago}}
    )
    incident_docs = await db.documents.count_documents(
        {"document_type": {"$in": INCIDENT_TYPES}, "status": "completed"}
    )
    chunks_indexed = await db.chunks.count_documents({})

    return {
        "documents_indexed": documents_indexed,
        "docs_this_week": docs_this_week,
        "incident_docs": incident_docs,
        "chunks_indexed": chunks_indexed,
    }
