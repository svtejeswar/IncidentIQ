from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from application.interfaces.vector_store_provider import IVectorStoreProvider, ScoredChunk
from core.logging.logger import get_logger

log = get_logger(__name__)


class MongoVectorStore(IVectorStoreProvider):
    def __init__(self, db: AsyncIOMotorDatabase, index_name: str) -> None:
        self._collection = db["chunks"]
        self._index_name = index_name

    async def upsert(
        self,
        chunk_id: str,
        document_id: str,
        document_type: str,
        text: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> None:
        doc = {
            "_id": chunk_id,
            "document_id": document_id,
            "document_type": document_type,
            "text": text,
            "embedding": embedding,
            "metadata": metadata or {},
        }
        await self._collection.replace_one({"_id": chunk_id}, doc, upsert=True)

    async def upsert_batch(self, records: list[dict]) -> None:
        if not records:
            return
        from pymongo import UpdateOne
        operations = [
            UpdateOne({"_id": r["chunk_id"]}, {"$set": {
                "document_id": r["document_id"],
                "document_type": r["document_type"],
                "text": r["text"],
                "embedding": r["embedding"],
                "metadata": r.get("metadata", {}),
            }}, upsert=True)
            for r in records
        ]
        await self._collection.bulk_write(operations, ordered=False)

    async def similarity_search(
        self,
        query_vector: list[float],
        limit: int = 10,
        document_type_filter: list[str] | None = None,
    ) -> list[ScoredChunk]:
        pipeline: list[dict] = [
            {
                "$vectorSearch": {
                    "index": self._index_name,
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": limit * 10,
                    "limit": limit,
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "document_id": 1,
                    "document_type": 1,
                    "text": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]

        if document_type_filter:
            pipeline.insert(1, {"$match": {"document_type": {"$in": document_type_filter}}})

        results = []
        async for doc in self._collection.aggregate(pipeline):
            results.append(
                ScoredChunk(
                    chunk_id=doc["_id"],
                    document_id=doc["document_id"],
                    document_type=doc.get("document_type", ""),
                    text=doc["text"],
                    score=doc.get("score", 0.0),
                    metadata=doc.get("metadata", {}),
                )
            )
        return results

    async def delete_by_document_id(self, document_id: str) -> int:
        result = await self._collection.delete_many({"document_id": document_id})
        return result.deleted_count
