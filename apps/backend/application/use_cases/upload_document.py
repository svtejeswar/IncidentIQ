from __future__ import annotations

from dataclasses import dataclass

from application.services.document_service import DocumentService
from domain.entities.document import Document
from domain.value_objects.document_type import DocumentType


@dataclass
class UploadDocumentCommand:
    file_data: bytes
    filename: str
    content_type: str
    document_type: DocumentType
    title: str | None = None
    uploaded_by: str = "anonymous"


class UploadDocumentUseCase:
    def __init__(self, document_service: DocumentService) -> None:
        self._service = document_service

    async def execute(self, command: UploadDocumentCommand) -> Document:
        return await self._service.upload_document(
            file_data=command.file_data,
            filename=command.filename,
            content_type=command.content_type,
            document_type=command.document_type,
            title=command.title,
            uploaded_by=command.uploaded_by,
        )
