"""Unit tests for the Document domain entity."""
from __future__ import annotations

from uuid import UUID

import pytest

from domain.entities.document import Document
from domain.enums.document_status import DocumentStatus
from domain.value_objects.document_type import DocumentType


def _make_document(**overrides) -> Document:
    defaults = dict(
        title="Database failover postmortem",
        document_type=DocumentType.POSTMORTEM,
        filename="postmortem.pdf",
        file_size=204_800,
        content_type="application/pdf",
    )
    defaults.update(overrides)
    return Document.create(**defaults)


class TestDocumentCreate:
    def test_returns_document_with_pending_status(self):
        doc = _make_document()
        assert doc.status == DocumentStatus.PENDING

    def test_generates_unique_ids(self):
        doc1 = _make_document()
        doc2 = _make_document()
        assert doc1.id != doc2.id

    def test_id_is_uuid(self):
        doc = _make_document()
        assert isinstance(doc.id, UUID)

    def test_default_uploaded_by_is_anonymous(self):
        doc = _make_document()
        assert doc.uploaded_by == "anonymous"

    def test_custom_uploaded_by(self):
        doc = _make_document(uploaded_by="sre-team")
        assert doc.uploaded_by == "sre-team"

    def test_chunk_count_starts_at_zero(self):
        doc = _make_document()
        assert doc.chunk_count == 0

    def test_error_message_is_none_on_creation(self):
        doc = _make_document()
        assert doc.error_message is None

    def test_file_path_is_none_on_creation(self):
        doc = _make_document()
        assert doc.file_path is None


class TestDocumentStatusTransitions:
    def test_mark_processing_sets_status(self):
        doc = _make_document()
        doc.mark_processing()
        assert doc.status == DocumentStatus.PROCESSING

    def test_mark_completed_sets_status_and_chunk_count(self):
        doc = _make_document()
        doc.mark_processing()
        doc.mark_completed(chunk_count=42)
        assert doc.status == DocumentStatus.COMPLETED
        assert doc.chunk_count == 42

    def test_mark_failed_sets_status_and_error(self):
        doc = _make_document()
        doc.mark_processing()
        doc.mark_failed("Embedding model unavailable")
        assert doc.status == DocumentStatus.FAILED
        assert doc.error_message == "Embedding model unavailable"

    def test_mark_processing_updates_updated_at(self):
        doc = _make_document()
        before = doc.updated_at
        doc.mark_processing()
        assert doc.updated_at >= before

    def test_mark_completed_updates_updated_at(self):
        doc = _make_document()
        doc.mark_processing()
        before = doc.updated_at
        doc.mark_completed(chunk_count=10)
        assert doc.updated_at >= before

    def test_mark_failed_updates_updated_at(self):
        doc = _make_document()
        before = doc.updated_at
        doc.mark_failed("error")
        assert doc.updated_at >= before


class TestDocumentIsProcessable:
    def test_pending_document_is_processable(self):
        doc = _make_document()
        assert doc.is_processable() is True

    def test_completed_document_is_not_processable(self):
        doc = _make_document()
        doc.mark_processing()
        doc.mark_completed(chunk_count=5)
        assert doc.is_processable() is False

    def test_processing_document_is_not_processable(self):
        doc = _make_document()
        doc.mark_processing()
        assert doc.is_processable() is False

    def test_failed_document_is_processable(self):
        """Failed documents can be retried."""
        doc = _make_document()
        doc.mark_failed("transient error")
        assert doc.is_processable() is True
