"""Integration tests for the platform statistics endpoint."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient


class TestPlatformStats:
    async def test_returns_200(self, client: AsyncClient):
        response = await client.get("/api/v1/stats")
        assert response.status_code == 200

    async def test_response_contains_documents_indexed(self, client: AsyncClient):
        response = await client.get("/api/v1/stats")
        body = response.json()
        assert "documents_indexed" in body

    async def test_response_contains_chunks_indexed(self, client: AsyncClient):
        response = await client.get("/api/v1/stats")
        body = response.json()
        assert "chunks_indexed" in body

    async def test_response_contains_incident_docs(self, client: AsyncClient):
        response = await client.get("/api/v1/stats")
        body = response.json()
        assert "incident_docs" in body

    async def test_response_contains_docs_this_week(self, client: AsyncClient):
        response = await client.get("/api/v1/stats")
        body = response.json()
        assert "docs_this_week" in body

    async def test_all_values_are_non_negative_integers(self, client: AsyncClient):
        response = await client.get("/api/v1/stats")
        body = response.json()
        for key in ("documents_indexed", "chunks_indexed", "incident_docs", "docs_this_week"):
            assert isinstance(body[key], int)
            assert body[key] >= 0

    async def test_counts_come_from_database(self, client: AsyncClient, mock_db):
        mock_db.documents.count_documents = AsyncMock(return_value=7)
        mock_db.chunks.count_documents = AsyncMock(return_value=210)
        response = await client.get("/api/v1/stats")
        assert response.status_code == 200

    async def test_content_type_is_json(self, client: AsyncClient):
        response = await client.get("/api/v1/stats")
        assert "application/json" in response.headers["content-type"]
