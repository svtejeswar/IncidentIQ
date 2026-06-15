from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.incident import Incident


class IIncidentRepository(ABC):
    @abstractmethod
    async def save(self, incident: Incident) -> Incident: ...

    @abstractmethod
    async def get_by_id(self, incident_id: UUID) -> Incident | None: ...

    @abstractmethod
    async def get_by_document_id(self, document_id: UUID) -> list[Incident]: ...

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 20) -> list[Incident]: ...

    @abstractmethod
    async def delete_by_document_id(self, document_id: UUID) -> int: ...
