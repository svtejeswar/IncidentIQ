from __future__ import annotations

import time
from uuid import UUID

from application.dto.search_dto import (
    IncidentResult,
    SearchRequest,
    SearchResponse,
    SimilarIncidentResult,
    SimilarIncidentsResponse,
)
from application.interfaces.embedding_provider import IEmbeddingProvider
from application.interfaces.llm_provider import ILLMProvider, LLMMessage
from application.interfaces.vector_store_provider import IVectorStoreProvider
from core.constants.constants import (
    RAG_CONTEXT_MAX_CHARS,
    RAG_CONTEXT_MAX_CHUNKS,
    SYSTEM_PROMPT,
)
from core.logging.logger import get_logger
from domain.repositories.document_repository import IDocumentRepository
from domain.value_objects.document_type import DocumentType
from domain.value_objects.severity import Severity

log = get_logger(__name__)


class SearchService:
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

    async def search(self, request: SearchRequest) -> SearchResponse:
        start_ms = int(time.monotonic() * 1000)

        query_vector = await self._embeddings.encode(request.query)

        doc_type_filter = (
            [dt.value for dt in request.document_types]
            if request.document_types
            else None
        )

        scored_chunks = await self._vector_store.similarity_search(
            query_vector=query_vector,
            limit=request.limit * 2,
            document_type_filter=doc_type_filter,
        )

        seen_doc_ids: set[str] = set()
        top_chunks = []
        for chunk in scored_chunks:
            if chunk.document_id not in seen_doc_ids:
                seen_doc_ids.add(chunk.document_id)
                top_chunks.append(chunk)
            if len(top_chunks) >= request.limit:
                break

        results: list[IncidentResult] = []
        for chunk in top_chunks:
            try:
                doc_uuid = UUID(chunk.document_id)
                document = await self._document_repo.get_by_id(doc_uuid)
                if document:
                    results.append(
                        IncidentResult(
                            document_id=doc_uuid,
                            title=document.title,
                            document_type=document.document_type,
                            relevance_score=round(chunk.score, 4),
                            excerpt=chunk.text[:300] + "..." if len(chunk.text) > 300 else chunk.text,
                            affected_services=chunk.metadata.get("affected_services", []),
                            severity=Severity(chunk.metadata.get("severity", "unknown")),
                            root_cause=chunk.metadata.get("root_cause"),
                            resolution=chunk.metadata.get("resolution"),
                        )
                    )
            except Exception as exc:
                log.warning("result_hydration_failed", chunk_id=chunk.chunk_id, error=str(exc))

        ai_answer: str | None = None
        if request.include_ai_answer and results:
            ai_answer = await self._generate_rag_answer(request.query, top_chunks)

        latency = int(time.monotonic() * 1000) - start_ms
        return SearchResponse(
            query=request.query,
            ai_answer=ai_answer,
            results=results,
            total_results=len(results),
            search_latency_ms=latency,
        )

    async def find_similar(
        self,
        document_id: UUID | None = None,
        text: str | None = None,
        limit: int = 5,
    ) -> SimilarIncidentsResponse:
        if document_id:
            document = await self._document_repo.get_by_id(document_id)
            if not document:
                return SimilarIncidentsResponse(similar_incidents=[], total=0)
            query_text = document.title
        elif text:
            query_text = text
        else:
            return SimilarIncidentsResponse(similar_incidents=[], total=0)

        query_vector = await self._embeddings.encode(query_text)
        scored_chunks = await self._vector_store.similarity_search(
            query_vector=query_vector, limit=limit * 3
        )

        exclude_id = str(document_id) if document_id else None
        seen: dict[str, SimilarIncidentResult] = {}

        for chunk in scored_chunks:
            if chunk.document_id == exclude_id:
                continue
            if chunk.document_id in seen:
                continue

            try:
                doc = await self._document_repo.get_by_id(UUID(chunk.document_id))
                if doc:
                    seen[chunk.document_id] = SimilarIncidentResult(
                        document_id=UUID(chunk.document_id),
                        title=doc.title,
                        similarity_score=round(chunk.score, 4),
                        shared_services=chunk.metadata.get("affected_services", []),
                        resolution_summary=chunk.metadata.get("resolution"),
                    )
            except Exception as exc:
                log.warning("similar_hydration_failed", error=str(exc))

            if len(seen) >= limit:
                break

        similar = list(seen.values())
        return SimilarIncidentsResponse(similar_incidents=similar, total=len(similar))

    async def _generate_rag_answer(self, query: str, chunks) -> str:
        context_parts = []
        total_chars = 0
        for chunk in chunks[:RAG_CONTEXT_MAX_CHUNKS]:
            if total_chars + len(chunk.text) > RAG_CONTEXT_MAX_CHARS:
                break
            context_parts.append(chunk.text)
            total_chars += len(chunk.text)

        context = "\n\n---\n\n".join(context_parts)
        messages = [
            LLMMessage(role="system", content=SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=f"Context from our incident knowledge base:\n\n{context}\n\nQuestion: {query}",
            ),
        ]
        response = await self._llm.generate(messages)
        return response.content
