"""Integration tests for the document management endpoints."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from httpx import AsyncClient


DOCUMENT_ID = "00000000-0000-0000-0000-000000000001"


def _sample_document_response(**overrides) -> MagicMock:
    doc = MagicMock()
    doc.id = overrides.get("id", DOCUMENT_ID)
    doc.title = overrides.get("title", "Test Postmortem")
    doc.document_type = overrides.get("document_type", "postmortem")
    doc.filename = overrides.get("filename", "postmortem.txt")
    doc.file_size = overrides.get("file_size", 2048)
    doc.status = overrides.get("status", "pending")
    doc.chunk_count = overrides.get("chunk_count", 0)
    doc.stream_url = f"/api/v1/documents/{DOCUMENT_ID}/stream"
    doc.created_at = "2025-06-14T00:00:00Z"
    doc.updated_at = "2025-06-14T00:00:00Z"
    doc.error_message = None
    return doc


class TestUploadDocument:
    async def test_valid_upload_returns_202(
        self, client: AsyncClient, mock_upload_use_case
    ):
        mock_upload_use_case.execute = AsyncMock(
            return_value=_sample_document_response()
        )
        response = await client.post(
            "/api/v1/documents",
            files={"file": ("incident.txt", b"Incident report content", "text/plain")},
            data={"document_type": "incident_report", "title": "Test Incident"},
        )
        assert response.status_code == 202

    async def test_upload_response_contains_stream_url(
        self, client: AsyncClient, mock_upload_use_case
    ):
        mock_upload_use_case.execute = AsyncMock(
            return_value=_sample_document_response()
        )
        response = await client.post(
            "/api/v1/documents",
            files={"file": ("test.txt", b"content", "text/plain")},
            data={"document_type": "runbook"},
        )
        assert response.status_code == 202
        body = response.json()
        assert "stream_url" in body

    async def test_upload_without_file_returns_422(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/documents",
            data={"document_type": "incident_report"},
        )
        assert response.status_code == 422

    async def test_upload_without_document_type_returns_422(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/documents",
            files={"file": ("test.txt", b"content", "text/plain")},
        )
        assert response.status_code == 422

    async def test_upload_invalid_document_type_returns_422(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/documents",
            files={"file": ("test.txt", b"content", "text/plain")},
            data={"document_type": "invalid_type_xyz"},
        )
        assert response.status_code == 422


class TestListDocuments:
    async def test_returns_200(self, client: AsyncClient, mock_document_service):
        mock_document_service.list_documents = AsyncMock(return_value=([], 0))
        response = await client.get("/api/v1/documents")
        assert response.status_code == 200

    async def test_returns_items_and_total(
        self, client: AsyncClient, mock_document_service
    ):
        doc = _sample_document_response()
        mock_document_service.list_documents = AsyncMock(return_value=([doc], 1))
        response = await client.get("/api/v1/documents")
        assert response.status_code == 200
        body = response.json()
        assert "items" in body
        assert "total" in body

    async def test_empty_list_returns_zero_total(
        self, client: AsyncClient, mock_document_service
    ):
        mock_document_service.list_documents = AsyncMock(return_value=([], 0))
        response = await client.get("/api/v1/documents")
        body = response.json()
        assert body["total"] == 0
        assert body["items"] == []

    async def test_pagination_params_accepted(
        self, client: AsyncClient, mock_document_service
    ):
        mock_document_service.list_documents = AsyncMock(return_value=([], 0))
        response = await client.get("/api/v1/documents?skip=10&limit=5")
        assert response.status_code == 200


class TestGetDocument:
    async def test_returns_200_when_found(
        self, client: AsyncClient, mock_document_service
    ):
        doc = _sample_document_response()
        mock_document_service.get_document = AsyncMock(return_value=doc)
        response = await client.get(f"/api/v1/documents/{DOCUMENT_ID}")
        assert response.status_code == 200

    async def test_returns_404_when_not_found(
        self, client: AsyncClient, mock_document_service
    ):
        mock_document_service.get_document = AsyncMock(return_value=None)
        response = await client.get(f"/api/v1/documents/{uuid4()}")
        assert response.status_code == 404

    async def test_invalid_uuid_returns_422(self, client: AsyncClient):
        response = await client.get("/api/v1/documents/not-a-uuid")
        assert response.status_code == 422


class TestDeleteDocument:
    async def test_returns_204_on_success(
        self, client: AsyncClient, mock_document_service
    ):
        mock_document_service.get_document = AsyncMock(
            return_value=_sample_document_response()
        )
        mock_document_service.delete_document = AsyncMock()
        response = await client.delete(f"/api/v1/documents/{DOCUMENT_ID}")
        assert response.status_code == 204

    async def test_returns_404_when_not_found(
        self, client: AsyncClient, mock_document_service
    ):
        mock_document_service.get_document = AsyncMock(return_value=None)
        response = await client.delete(f"/api/v1/documents/{uuid4()}")
        assert response.status_code == 404
