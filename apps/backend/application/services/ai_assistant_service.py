from __future__ import annotations

import uuid

from application.dto.assistant_dto import (
    ChatRequest,
    ChatResponse,
    SourceReference,
)
from application.interfaces.embedding_provider import IEmbeddingProvider
from application.interfaces.llm_provider import ILLMProvider, LLMMessage
from application.interfaces.vector_store_provider import IVectorStoreProvider
from core.constants.constants import RAG_CONTEXT_MAX_CHARS, RAG_CONTEXT_MAX_CHUNKS, SYSTEM_PROMPT
from core.logging.logger import get_logger
from domain.repositories.document_repository import IDocumentRepository
from domain.value_objects.document_type import DocumentType

log = get_logger(__name__)

RUNBOOK_TYPES = {DocumentType.RUNBOOK, DocumentType.TROUBLESHOOTING_GUIDE}


class AIAssistantService:
    def __init__(
        self,
        embedding_provider: IEmbeddingProvider,
        vector_store: IVectorStoreProvider,
        llm_provider: ILLMProvider,
        document_repo: IDocumentRepository,
    ) -> None:
        self._embeddings = embedding_provider
        self._vector_store = vector_store
        self._llm = llm_provider
        self._document_repo = document_repo

    async def chat(self, request: ChatRequest) -> ChatResponse:
        conversation_id = request.conversation_id or str(uuid.uuid4())

        query_vector = await self._embeddings.encode(request.message)
        scored_chunks = await self._vector_store.similarity_search(
            query_vector=query_vector, limit=RAG_CONTEXT_MAX_CHUNKS
        )

        context_parts = []
        total_chars = 0
        sources: list[SourceReference] = []
        runbooks: list[SourceReference] = []
        seen_doc_ids: set[str] = set()

        for chunk in scored_chunks:
            if total_chars + len(chunk.text) > RAG_CONTEXT_MAX_CHARS:
                break
            context_parts.append(chunk.text)
            total_chars += len(chunk.text)

            if chunk.document_id not in seen_doc_ids:
                seen_doc_ids.add(chunk.document_id)
                try:
                    from uuid import UUID
                    doc = await self._document_repo.get_by_id(UUID(chunk.document_id))
                    if doc:
                        ref = SourceReference(
                            document_id=doc.id,
                            title=doc.title,
                            excerpt=chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                            relevance_score=round(chunk.score, 4),
                        )
                        if doc.document_type in RUNBOOK_TYPES:
                            runbooks.append(ref)
                        else:
                            sources.append(ref)
                except Exception as exc:
                    log.warning("assistant_source_hydration_failed", error=str(exc))

        messages = self._build_messages(request, context_parts)
        response = await self._llm.generate(messages)

        return ChatResponse(
            conversation_id=conversation_id,
            answer=response.content,
            sources=sources[:5],
            suggested_runbooks=runbooks[:3],
        )

    def _build_messages(self, request: ChatRequest, context_parts: list[str]) -> list[LLMMessage]:
        messages: list[LLMMessage] = [LLMMessage(role="system", content=SYSTEM_PROMPT)]

        for hist_msg in request.history[-6:]:
            messages.append(LLMMessage(role=hist_msg.role, content=hist_msg.content))

        context = "\n\n---\n\n".join(context_parts)
        user_content = (
            f"Relevant knowledge base context:\n\n{context}\n\n"
            f"Question: {request.message}"
            if context_parts
            else request.message
        )
        messages.append(LLMMessage(role="user", content=user_content))
        return messages
