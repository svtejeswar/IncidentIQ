from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from domain.enums.document_status import DocumentStatus
from domain.value_objects.document_type import DocumentType


class DocumentCreateRequest(BaseModel):
    title: str | None = None
    document_type: DocumentType


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    document_type: DocumentType
    filename: str
    file_size: int
    status: DocumentStatus
    chunk_count: int
    uploaded_by: str
    created_at: datetime
    updated_at: datetime
    error_message: str | None = None
    stream_url: str | None = None


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    skip: int
    limit: int


class ProcessingEventResponse(BaseModel):
    stage: str
    message: str
    progress: int = Field(ge=0, le=100)
    chunk_count: int | None = None
    error: str | None = None
