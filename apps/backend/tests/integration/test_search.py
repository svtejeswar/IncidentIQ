"""Integration tests for semantic search and similar incident endpoints."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient


def _mock_search_response(**overrides) -> MagicMock:
    resp = MagicMock()
    resp.query = overrides.get("query", "test query")
    resp.ai_answer = overrides.get("ai_answer", "The root cause was a misconfigured timeout.")
    resp.results = overrides.get("results", [])
    resp.total_results = overrides.get("total_results", 0)
    resp.search_latency_ms = overrides.get("search_latency_ms", 38)
    return resp


def _mock_similar_response(**overrides) -> MagicMock:
    resp = MagicMock()
    resp.similar_incidents = overrides.get("similar_incidents", [])
    resp.total = overrides.get("total", 0)
    return resp


class TestSemanticSearch:
    async def test_valid_query_returns_200(
        self, client: AsyncClient, mock_search_use_case
    ):
        mock_search_use_case.execute = AsyncMock(
            return_value=_mock_search_response()
        )
        response = await client.post(
            "/api/v1/search",
            json={"query": "database connection pool exhaustion"},
        )
        assert response.status_code == 200

    async def test_response_contains_required_fields(
        self, client: AsyncClient, mock_search_use_case
    ):
        mock_search_use_case.execute = AsyncMock(
            return_value=_mock_search_response(query="postgres timeout")
        )
        response = await client.post(
            "/api/v1/search",
            json={"query": "postgres timeout"},
        )
        body = response.json()
        assert "query" in body
        assert "results" in body
        assert "total_results" in body
        assert "search_latency_ms" in body

    async def test_missing_query_returns_422(self, client: AsyncClient):
        response = await client.post("/api/v1/search", json={})
        assert response.status_code == 422

    async def test_empty_query_returns_422(self, client: AsyncClient):
        response = await client.post("/api/v1/search", json={"query": ""})
        assert response.status_code == 422

    async def test_with_ai_answer_flag(
        self, client: AsyncClient, mock_search_use_case
    ):
        mock_search_use_case.execute = AsyncMock(
            return_value=_mock_search_response(
                ai_answer="Based on 3 historical incidents…"
            )
        )
        response = await client.post(
            "/api/v1/search",
            json={"query": "redis cache miss", "include_ai_answer": True},
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("ai_answer") is not None

    async def test_with_limit_parameter(
        self, client: AsyncClient, mock_search_use_case
    ):
        mock_search_use_case.execute = AsyncMock(
            return_value=_mock_search_response()
        )
        response = await client.post(
            "/api/v1/search",
            json={"query": "memory leak", "limit": 3},
        )
        assert response.status_code == 200

    async def test_with_document_types_filter(
        self, client: AsyncClient, mock_search_use_case
    ):
        mock_search_use_case.execute = AsyncMock(
            return_value=_mock_search_response()
        )
        response = await client.post(
            "/api/v1/search",
            json={
                "query": "deployment failure",
                "document_types": ["postmortem", "rca"],
            },
        )
        assert response.status_code == 200

    async def test_invalid_content_type_returns_422(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/search",
            content=b"not json",
            headers={"Content-Type": "text/plain"},
        )
        assert response.status_code in (422, 400)


class TestSimilarIncidents:
    async def test_with_text_returns_200(
        self, client: AsyncClient, mock_similar_use_case
    ):
        mock_similar_use_case.execute = AsyncMock(
            return_value=_mock_similar_response()
        )
        response = await client.post(
            "/api/v1/search/similar",
            json={"text": "kafka consumer lag spike"},
        )
        assert response.status_code == 200

    async def test_with_document_id_returns_200(
        self, client: AsyncClient, mock_similar_use_case
    ):
        mock_similar_use_case.execute = AsyncMock(
            return_value=_mock_similar_response()
        )
        response = await client.post(
            "/api/v1/search/similar",
            json={"document_id": "00000000-0000-0000-0000-000000000001"},
        )
        assert response.status_code == 200

    async def test_response_contains_similar_incidents_and_total(
        self, client: AsyncClient, mock_similar_use_case
    ):
        mock_similar_use_case.execute = AsyncMock(
            return_value=_mock_similar_response()
        )
        response = await client.post(
            "/api/v1/search/similar",
            json={"text": "auth service crash"},
        )
        body = response.json()
        assert "similar_incidents" in body
        assert "total" in body

    async def test_neither_text_nor_id_returns_422(self, client: AsyncClient):
        response = await client.post("/api/v1/search/similar", json={})
        assert response.status_code == 422

    async def test_with_limit_parameter(
        self, client: AsyncClient, mock_similar_use_case
    ):
        mock_similar_use_case.execute = AsyncMock(
            return_value=_mock_similar_response()
        )
        response = await client.post(
            "/api/v1/search/similar",
            json={"text": "ssl certificate expired", "limit": 2},
        )
        assert response.status_code == 200
