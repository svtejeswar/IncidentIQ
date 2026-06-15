from __future__ import annotations

from datetime import datetime
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase

from domain.entities.incident import Incident
from domain.repositories.incident_repository import IIncidentRepository
from domain.value_objects.severity import Severity


class MongoIncidentRepository(IIncidentRepository):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db["incidents"]

    async def save(self, incident: Incident) -> Incident:
        await self._collection.insert_one(self._to_dict(incident))
        return incident

    async def get_by_id(self, incident_id: UUID) -> Incident | None:
        doc = await self._collection.find_one({"_id": str(incident_id)})
        return self._from_dict(doc) if doc else None

    async def get_by_document_id(self, document_id: UUID) -> list[Incident]:
        cursor = self._collection.find({"document_id": str(document_id)})
        return [self._from_dict(d) async for d in cursor]

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[Incident]:
        cursor = self._collection.find({}).sort("created_at", -1).skip(skip).limit(limit)
        return [self._from_dict(d) async for d in cursor]

    async def delete_by_document_id(self, document_id: UUID) -> int:
        result = await self._collection.delete_many({"document_id": str(document_id)})
        return result.deleted_count

    def _to_dict(self, incident: Incident) -> dict:
        return {
            "_id": str(incident.id),
            "document_id": str(incident.document_id),
            "title": incident.title,
            "description": incident.description,
            "root_cause": incident.root_cause,
            "resolution": incident.resolution,
            "impact": incident.impact,
            "preventive_actions": incident.preventive_actions,
            "affected_services": incident.affected_services,
            "severity": incident.severity.value,
            "occurred_at": incident.occurred_at,
            "created_at": incident.created_at,
        }

    def _from_dict(self, data: dict) -> Incident:
        return Incident(
            id=UUID(data["_id"]),
            document_id=UUID(data["document_id"]),
            title=data["title"],
            description=data.get("description", ""),
            root_cause=data.get("root_cause"),
            resolution=data.get("resolution"),
            impact=data.get("impact"),
            preventive_actions=data.get("preventive_actions", []),
            affected_services=data.get("affected_services", []),
            severity=Severity(data.get("severity", "unknown")),
            occurred_at=data.get("occurred_at"),
            created_at=data["created_at"],
        )
