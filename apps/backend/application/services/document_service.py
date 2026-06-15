from __future__ import annotations

import asyncio
from typing import AsyncGenerator
from uuid import UUID

from application.dto.document_dto import (
    DocumentCreateRequest,
    DocumentListResponse,
    DocumentResponse,
    ProcessingEventResponse,
)
from application.interfaces.file_storage import IFileStorage
from core.logging.logger import get_logger
from domain.entities.document import Document
from domain.enums.document_status import DocumentStatus
from domain.enums.processing_stage import ProcessingStage
from domain.exceptions.domain_exceptions import (
    DocumentNotFoundException,
    FileTooLargeException,
    UnsupportedFileTypeException,
)
from domain.repositories.chunk_repository import IChunkRepository
from domain.repositories.document_repository import IDocumentRepository
from domain.repositories.incident_repository import IIncidentRepository
from domain.value_objects.document_type import DocumentType

log = get_logger(__name__)

SUPPORTED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
}


class DocumentService:
    def __init__(
        self,
        document_repo: IDocumentRepository,
        chunk_repo: IChunkRepository,
        incident_repo: IIncidentRepository,
        file_storage: IFileStorage,
        max_file_size_bytes: int,
    ) -> None:
        self._document_repo = document_repo
        self._chunk_repo = chunk_repo
        self._incident_repo = incident_repo
        self._file_storage = file_storage
        self._max_file_size_bytes = max_file_size_bytes

    async def upload_document(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        document_type: DocumentType,
        title: str | None = None,
        uploaded_by: str = "anonymous",
    ) -> Document:
        if len(file_data) > self._max_file_size_bytes:
            raise FileTooLargeException(len(file_data), self._max_file_size_bytes)

        if content_type not in SUPPORTED_CONTENT_TYPES:
            raise UnsupportedFileTypeException(content_type)

        file_path = await self._file_storage.save(file_data, filename)

        document = Document.create(
            title=title or filename,
            document_type=document_type,
            filename=filename,
            file_size=len(file_data),
            content_type=content_type,
            uploaded_by=uploaded_by,
        )
        document.file_path = file_path

        saved = await self._document_repo.save(document)
        log.info("document_uploaded", document_id=str(saved.id), title=saved.title)
        return saved

    async def get_document(self, document_id: UUID) -> Document:
        document = await self._document_repo.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundException(str(document_id))
        return document

    async def list_documents(
        self,
        skip: int = 0,
        limit: int = 20,
        status: DocumentStatus | None = None,
    ) -> DocumentListResponse:
        documents = await self._document_repo.list_all(skip=skip, limit=limit, status=status)
        total = await self._document_repo.count()
        return DocumentListResponse(
            items=[self._to_response(d) for d in documents],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def delete_document(self, document_id: UUID) -> None:
        document = await self._document_repo.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundException(str(document_id))

        await self._chunk_repo.delete_by_document_id(document_id)
        await self._incident_repo.delete_by_document_id(document_id)

        if document.file_path:
            await self._file_storage.delete(document.file_path)

        await self._document_repo.delete(document_id)
        log.info("document_deleted", document_id=str(document_id))

    async def stream_processing_events(
        self, document_id: UUID
    ) -> AsyncGenerator[ProcessingEventResponse, None]:
        """Yields processing stage events. Used by SSE route."""
        events: asyncio.Queue[ProcessingEventResponse | None] = asyncio.Queue()
        self._event_queues[str(document_id)] = events

        try:
            while True:
                event = await events.get()
                if event is None:
                    break
                yield event
        finally:
            self._event_queues.pop(str(document_id), None)

    async def emit_processing_event(
        self,
        document_id: str,
        stage: ProcessingStage,
        message: str,
        progress: int,
        chunk_count: int | None = None,
    ) -> None:
        event = ProcessingEventResponse(
            stage=stage.value,
            message=message,
            progress=progress,
            chunk_count=chunk_count,
        )
        queue = self._event_queues.get(document_id)
        if queue:
            await queue.put(event)
        if stage in {ProcessingStage.COMPLETED, ProcessingStage.FAILED}:
            if queue:
                await queue.put(None)

    def _to_response(self, document: Document) -> DocumentResponse:
        return DocumentResponse(
            id=document.id,
            title=document.title,
            document_type=document.document_type,
            filename=document.filename,
            file_size=document.file_size,
            status=document.status,
            chunk_count=document.chunk_count,
            uploaded_by=document.uploaded_by,
            created_at=document.created_at,
            updated_at=document.updated_at,
            error_message=document.error_message,
            stream_url=f"/api/v1/documents/{document.id}/stream",
        )

    _event_queues: dict[str, asyncio.Queue] = {}
