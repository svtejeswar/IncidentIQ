from __future__ import annotations

import asyncio
import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from api.dependencies.providers import (
    get_chunk_repo,
    get_document_repo,
    get_document_service,
    get_embedding_provider,
    get_upload_use_case,
    get_vector_store,
)
from application.dto.document_dto import DocumentListResponse, DocumentResponse
from application.services.document_service import DocumentService
from application.use_cases.upload_document import UploadDocumentCommand, UploadDocumentUseCase
from core.config.settings import get_settings
from core.logging.logger import get_logger
from domain.enums.document_status import DocumentStatus
from domain.exceptions.domain_exceptions import (
    DocumentNotFoundException,
    FileTooLargeException,
    UnsupportedFileTypeException,
)
from domain.value_objects.document_type import DocumentType
from ingestion.pipelines.document_pipeline import DocumentIngestionPipeline

log = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File()],
    document_type: Annotated[DocumentType, Form()],
    title: Annotated[str | None, Form()] = None,
    use_case: Annotated[UploadDocumentUseCase, Depends(get_upload_use_case)] = None,
    doc_service: Annotated[DocumentService, Depends(get_document_service)] = None,
) -> DocumentResponse:
    file_data = await file.read()

    try:
        document = await use_case.execute(
            UploadDocumentCommand(
                file_data=file_data,
                filename=file.filename or "unknown",
                content_type=file.content_type or "application/octet-stream",
                document_type=document_type,
                title=title,
            )
        )
    except UnsupportedFileTypeException as e:
        raise HTTPException(status_code=415, detail=e.message)
    except FileTooLargeException as e:
        raise HTTPException(status_code=413, detail=e.message)

    settings = get_settings()
    pipeline = DocumentIngestionPipeline(
        document_repo=get_document_repo(),
        chunk_repo=get_chunk_repo(),
        embedding_provider=get_embedding_provider(),
        vector_store=get_vector_store(),
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    background_tasks.add_task(
        pipeline.run,
        document,
        doc_service.emit_processing_event,
    )

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
        stream_url=f"/api/v1/documents/{document.id}/stream",
    )


@router.get("/{document_id}/stream")
async def stream_processing(
    document_id: UUID,
    doc_service: Annotated[DocumentService, Depends(get_document_service)],
) -> StreamingResponse:
    async def event_generator():
        async for event in doc_service.stream_processing_events(document_id):
            data = json.dumps(event.model_dump())
            yield f"data: {data}\n\n"
            await asyncio.sleep(0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    status: DocumentStatus | None = None,
    doc_service: Annotated[DocumentService, Depends(get_document_service)] = None,
) -> DocumentListResponse:
    return await doc_service.list_documents(skip=skip, limit=limit, status=status)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    doc_service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentResponse:
    try:
        document = await doc_service.get_document(document_id)
    except DocumentNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)

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


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_document(
    document_id: UUID,
    doc_service: Annotated[DocumentService, Depends(get_document_service)],
) -> None:
    try:
        await doc_service.delete_document(document_id)
    except DocumentNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
