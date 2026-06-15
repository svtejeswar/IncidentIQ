from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.document import Document
from domain.enums.document_status import DocumentStatus


class IDocumentRepository(ABC):
    @abstractmethod
    async def save(self, document: Document) -> Document: ...

    @abstractmethod
    async def get_by_id(self, document_id: UUID) -> Document | None: ...

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: DocumentStatus | None = None,
    ) -> list[Document]: ...

    @abstractmethod
    async def update(self, document: Document) -> Document: ...

    @abstractmethod
    async def delete(self, document_id: UUID) -> bool: ...

    @abstractmethod
    async def count(self) -> int: ...
