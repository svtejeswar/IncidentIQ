from __future__ import annotations

from datetime import datetime
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase

from domain.entities.document import Document
from domain.enums.document_status import DocumentStatus
from domain.repositories.document_repository import IDocumentRepository
from domain.value_objects.document_type import DocumentType


class MongoDocumentRepository(IDocumentRepository):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db["documents"]

    async def save(self, document: Document) -> Document:
        doc = self._to_dict(document)
        await self._collection.insert_one(doc)
        return document

    async def get_by_id(self, document_id: UUID) -> Document | None:
        doc = await self._collection.find_one({"_id": str(document_id)})
        return self._from_dict(doc) if doc else None

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: DocumentStatus | None = None,
    ) -> list[Document]:
        query = {}
        if status:
            query["status"] = status.value
        cursor = self._collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        return [self._from_dict(d) async for d in cursor]

    async def update(self, document: Document) -> Document:
        doc = self._to_dict(document)
        await self._collection.replace_one({"_id": doc["_id"]}, doc)
        return document

    async def delete(self, document_id: UUID) -> bool:
        result = await self._collection.delete_one({"_id": str(document_id)})
        return result.deleted_count > 0

    async def count(self) -> int:
        return await self._collection.count_documents({})

    def _to_dict(self, document: Document) -> dict:
        return {
            "_id": str(document.id),
            "title": document.title,
            "document_type": document.document_type.value,
            "filename": document.filename,
            "file_size": document.file_size,
            "content_type": document.content_type,
            "uploaded_by": document.uploaded_by,
            "status": document.status.value,
            "chunk_count": document.chunk_count,
            "file_path": document.file_path,
            "error_message": document.error_message,
            "created_at": document.created_at,
            "updated_at": document.updated_at,
        }

    def _from_dict(self, data: dict) -> Document:
        return Document(
            id=UUID(data["_id"]),
            title=data["title"],
            document_type=DocumentType(data["document_type"]),
            filename=data["filename"],
            file_size=data["file_size"],
            content_type=data["content_type"],
            uploaded_by=data["uploaded_by"],
            status=DocumentStatus(data["status"]),
            chunk_count=data.get("chunk_count", 0),
            file_path=data.get("file_path"),
            error_message=data.get("error_message"),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )
