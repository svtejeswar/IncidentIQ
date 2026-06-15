"""Integration tests for health check endpoints."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


class TestLivenessProbe:
    async def test_returns_200(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200

    async def test_response_contains_status_ok(self, client: AsyncClient):
        response = await client.get("/health")
        body = response.json()
        assert body.get("status") == "ok"

    async def test_response_contains_version(self, client: AsyncClient):
        response = await client.get("/health")
        body = response.json()
        assert "version" in body

    async def test_content_type_is_json(self, client: AsyncClient):
        response = await client.get("/health")
        assert "application/json" in response.headers["content-type"]


class TestReadinessProbe:
    async def test_returns_200_when_db_responds(self, client: AsyncClient, mock_db):
        mock_db.command = AsyncMock(return_value={"ok": 1})
        response = await client.get("/health/ready")
        assert response.status_code == 200

    async def test_response_contains_status_ready(self, client: AsyncClient, mock_db):
        mock_db.command = AsyncMock(return_value={"ok": 1})
        response = await client.get("/health/ready")
        body = response.json()
        assert body.get("status") in ("ok", "ready")

    async def test_returns_503_when_db_unavailable(self, client: AsyncClient, mock_db):
        mock_db.command = AsyncMock(side_effect=Exception("Connection refused"))
        response = await client.get("/health/ready")
        assert response.status_code == 503
