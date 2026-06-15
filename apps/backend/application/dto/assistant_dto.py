from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None
    history: list[ChatMessage] = []


class SourceReference(BaseModel):
    document_id: UUID
    title: str
    excerpt: str
    relevance_score: float


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: list[SourceReference] = []
    suggested_runbooks: list[SourceReference] = []
