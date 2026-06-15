from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ScoredChunk:
    chunk_id: str
    document_id: str
    document_type: str
    text: str
    score: float
    metadata: dict


class IVectorStoreProvider(ABC):
    @abstractmethod
    async def upsert(
        self,
        chunk_id: str,
        document_id: str,
        document_type: str,
        text: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> None: ...

    @abstractmethod
    async def upsert_batch(
        self,
        records: list[dict],
    ) -> None: ...

    @abstractmethod
    async def similarity_search(
        self,
        query_vector: list[float],
        limit: int = 10,
        document_type_filter: list[str] | None = None,
    ) -> list[ScoredChunk]: ...

    @abstractmethod
    async def delete_by_document_id(self, document_id: str) -> int: ...
