from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from domain.enums.document_status import DocumentStatus
from domain.value_objects.document_type import DocumentType


@dataclass
class Document:
    id: UUID
    title: str
    document_type: DocumentType
    filename: str
    file_size: int
    content_type: str
    uploaded_by: str
    status: DocumentStatus
    chunk_count: int
    created_at: datetime
    updated_at: datetime
    file_path: str | None = None
    error_message: str | None = None

    @classmethod
    def create(
        cls,
        title: str,
        document_type: DocumentType,
        filename: str,
        file_size: int,
        content_type: str,
        uploaded_by: str = "anonymous",
    ) -> Document:
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            title=title,
            document_type=document_type,
            filename=filename,
            file_size=file_size,
            content_type=content_type,
            uploaded_by=uploaded_by,
            status=DocumentStatus.PENDING,
            chunk_count=0,
            created_at=now,
            updated_at=now,
        )

    def mark_processing(self) -> None:
        self.status = DocumentStatus.PROCESSING
        self.updated_at = datetime.utcnow()

    def mark_completed(self, chunk_count: int) -> None:
        self.status = DocumentStatus.COMPLETED
        self.chunk_count = chunk_count
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        self.status = DocumentStatus.FAILED
        self.error_message = error
        self.updated_at = datetime.utcnow()

    def is_processable(self) -> bool:
        return self.status in {DocumentStatus.PENDING, DocumentStatus.FAILED}
