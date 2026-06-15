from __future__ import annotations

from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase

from domain.entities.chunk import Chunk
from domain.repositories.chunk_repository import IChunkRepository


class MongoChunkRepository(IChunkRepository):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db["chunks"]

    async def save_batch(self, chunks: list[Chunk]) -> list[Chunk]:
        if not chunks:
            return []
        docs = [self._to_dict(c) for c in chunks]
        await self._collection.insert_many(docs)
        return chunks

    async def get_by_document_id(self, document_id: UUID) -> list[Chunk]:
        cursor = self._collection.find(
            {"document_id": str(document_id)}
        ).sort("chunk_index", 1)
        return [self._from_dict(d) async for d in cursor]

    async def delete_by_document_id(self, document_id: UUID) -> int:
        result = await self._collection.delete_many({"document_id": str(document_id)})
        return result.deleted_count

    async def count_by_document_id(self, document_id: UUID) -> int:
        return await self._collection.count_documents({"document_id": str(document_id)})

    def _to_dict(self, chunk: Chunk) -> dict:
        return {
            "_id": str(chunk.id),
            "document_id": str(chunk.document_id),
            "chunk_index": chunk.chunk_index,
            "text": chunk.text,
            "embedding": chunk.embedding,
            "document_type": chunk.document_type,
            "metadata": chunk.metadata,
        }

    def _from_dict(self, data: dict) -> Chunk:
        return Chunk(
            id=UUID(data["_id"]),
            document_id=UUID(data["document_id"]),
            chunk_index=data["chunk_index"],
            text=data["text"],
            embedding=data.get("embedding", []),
            document_type=data.get("document_type", ""),
            metadata=data.get("metadata", {}),
        )
