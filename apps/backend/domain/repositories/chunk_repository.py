from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.chunk import Chunk


class IChunkRepository(ABC):
    @abstractmethod
    async def save_batch(self, chunks: list[Chunk]) -> list[Chunk]: ...

    @abstractmethod
    async def get_by_document_id(self, document_id: UUID) -> list[Chunk]: ...

    @abstractmethod
    async def delete_by_document_id(self, document_id: UUID) -> int: ...

    @abstractmethod
    async def count_by_document_id(self, document_id: UUID) -> int: ...
