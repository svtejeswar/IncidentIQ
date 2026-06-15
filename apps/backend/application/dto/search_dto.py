from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from domain.value_objects.document_type import DocumentType
from domain.value_objects.severity import Severity


class SearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)
    document_types: list[DocumentType] | None = None
    include_ai_answer: bool = True


class SimilarIncidentRequest(BaseModel):
    document_id: UUID | None = None
    text: str | None = None
    limit: int = Field(default=5, ge=1, le=10)


class IncidentResult(BaseModel):
    document_id: UUID
    title: str
    document_type: DocumentType
    relevance_score: float
    excerpt: str
    root_cause: str | None = None
    resolution: str | None = None
    affected_services: list[str] = []
    severity: Severity = Severity.UNKNOWN


class SearchResponse(BaseModel):
    query: str
    ai_answer: str | None = None
    results: list[IncidentResult]
    total_results: int
    search_latency_ms: int


class SimilarIncidentResult(BaseModel):
    document_id: UUID
    title: str
    similarity_score: float
    shared_services: list[str] = []
    resolution_summary: str | None = None


class SimilarIncidentsResponse(BaseModel):
    similar_incidents: list[SimilarIncidentResult]
    total: int
