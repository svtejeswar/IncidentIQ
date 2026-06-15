"""
Shared fixtures for the IncidentIQ test suite.

Tests are in two tiers:
  unit/        Pure Python — no I/O, no mocks needed.
  integration/ HTTP layer — all external deps replaced with AsyncMocks via DI overrides.

Integration tests patch the MongoDB lifespan connection so no real database
is required. Each test service mock starts with sensible defaults; individual
tests can override return values as needed.
"""
from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Must be set before any app import so Pydantic BaseSettings reads them.
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("GROQ_API_KEY", "gsk_test_placeholder_key")
os.environ.setdefault("APP_SECRET_KEY", "test-secret-key-32-characters-xx")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DEBUG", "false")

from api.dependencies.providers import (  # noqa: E402
    get_assistant_service,
    get_assistant_use_case,
    get_document_service,
    get_search_service,
    get_search_use_case,
    get_similar_use_case,
    get_upload_use_case,
)
from main import app  # noqa: E402


# ---------------------------------------------------------------------------
# Service mocks — returned by DI overrides in integration tests
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_document_service() -> MagicMock:
    svc = MagicMock()
    svc.list_documents = AsyncMock(return_value=([], 0))
    svc.get_document = AsyncMock(return_value=None)
    svc.delete_document = AsyncMock()
    return svc


@pytest.fixture
def mock_upload_use_case() -> MagicMock:
    uc = MagicMock()
    uc.execute = AsyncMock(return_value=MagicMock(
        id="00000000-0000-0000-0000-000000000001",
        title="Test Document",
        document_type="incident_report",
        filename="test.txt",
        file_size=1024,
        status="pending",
        chunk_count=0,
        stream_url="/api/v1/documents/00000000-0000-0000-0000-000000000001/stream",
        created_at="2025-06-14T00:00:00Z",
        updated_at="2025-06-14T00:00:00Z",
    ))
    return uc


@pytest.fixture
def mock_search_use_case() -> MagicMock:
    uc = MagicMock()
    uc.execute = AsyncMock(return_value=MagicMock(
        query="test query",
        ai_answer="Based on historical incidents, the root cause was…",
        results=[],
        total_results=0,
        search_latency_ms=42,
    ))
    return uc


@pytest.fixture
def mock_similar_use_case() -> MagicMock:
    uc = MagicMock()
    uc.execute = AsyncMock(return_value=MagicMock(
        similar_incidents=[],
        total=0,
    ))
    return uc


@pytest.fixture
def mock_assistant_use_case() -> MagicMock:
    uc = MagicMock()
    uc.execute = AsyncMock(return_value=MagicMock(
        conversation_id="conv-test-001",
        answer="Here is what the knowledge base says…",
        sources=[],
        suggested_runbooks=[],
    ))
    return uc


# ---------------------------------------------------------------------------
# Mock database for stats endpoint (uses get_database() directly)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    db.documents.count_documents = AsyncMock(return_value=5)
    db.chunks.count_documents = AsyncMock(return_value=120)
    db.command = AsyncMock(return_value={"ok": 1})
    return db


# ---------------------------------------------------------------------------
# HTTP test client — all external dependencies are mocked
# ---------------------------------------------------------------------------

@pytest.fixture
async def client(
    mock_document_service,
    mock_upload_use_case,
    mock_search_use_case,
    mock_similar_use_case,
    mock_assistant_use_case,
    mock_db,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP test client with:
    - MongoDB lifespan connect/disconnect patched to no-ops
    - get_database() patched to return mock_db
    - All FastAPI service/use-case dependencies overridden with mocks
    """
    app.dependency_overrides[get_document_service] = lambda: mock_document_service
    app.dependency_overrides[get_upload_use_case] = lambda: mock_upload_use_case
    app.dependency_overrides[get_search_use_case] = lambda: mock_search_use_case
    app.dependency_overrides[get_similar_use_case] = lambda: mock_similar_use_case
    app.dependency_overrides[get_assistant_use_case] = lambda: mock_assistant_use_case
    app.dependency_overrides[get_search_service] = lambda: MagicMock()
    app.dependency_overrides[get_assistant_service] = lambda: MagicMock()

    with (
        patch("main.connect", new_callable=AsyncMock),
        patch("main.disconnect", new_callable=AsyncMock),
        patch(
            "infrastructure.database.mongodb.client.get_database",
            return_value=mock_db,
        ),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    app.dependency_overrides.clear()
