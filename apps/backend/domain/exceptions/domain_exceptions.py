class DomainException(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str, code: str = "DOMAIN_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class DocumentNotFoundException(DomainException):
    def __init__(self, document_id: str) -> None:
        super().__init__(f"Document not found: {document_id}", "NOT_FOUND")
        self.document_id = document_id


class DocumentAlreadyProcessingException(DomainException):
    def __init__(self, document_id: str) -> None:
        super().__init__(
            f"Document is already being processed: {document_id}",
            "ALREADY_PROCESSING",
        )


class UnsupportedFileTypeException(DomainException):
    def __init__(self, content_type: str) -> None:
        super().__init__(
            f"Unsupported file type: {content_type}",
            "UNSUPPORTED_FILE_TYPE",
        )


class FileTooLargeException(DomainException):
    def __init__(self, size_bytes: int, max_bytes: int) -> None:
        super().__init__(
            f"File size {size_bytes} exceeds maximum {max_bytes}",
            "FILE_TOO_LARGE",
        )


class ExtractionFailedException(DomainException):
    def __init__(self, filename: str, reason: str) -> None:
        super().__init__(
            f"Failed to extract text from {filename}: {reason}",
            "EXTRACTION_FAILED",
        )


class EmbeddingFailedException(DomainException):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Embedding generation failed: {reason}", "EMBEDDING_FAILED")


class SearchFailedException(DomainException):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Search failed: {reason}", "SEARCH_FAILED")
