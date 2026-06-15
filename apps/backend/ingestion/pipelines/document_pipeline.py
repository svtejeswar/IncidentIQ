from __future__ import annotations

import uuid
from collections.abc import Awaitable
from typing import Callable

from application.interfaces.embedding_provider import IEmbeddingProvider
from application.interfaces.vector_store_provider import IVectorStoreProvider
from core.logging.logger import get_logger
from domain.entities.chunk import Chunk
from domain.entities.document import Document
from domain.enums.processing_stage import ProcessingStage
from domain.repositories.chunk_repository import IChunkRepository
from domain.repositories.document_repository import IDocumentRepository
from ingestion.chunkers.text_chunker import TextChunker
from ingestion.enrichers.metadata_enricher import MetadataEnricher
from ingestion.extractors.text_extractor import TextExtractorDispatcher

log = get_logger(__name__)

ProgressCallback = Callable[[str, ProcessingStage, str, int], Awaitable[None]]


class DocumentIngestionPipeline:
    def __init__(
        self,
        document_repo: IDocumentRepository,
        chunk_repo: IChunkRepository,
        embedding_provider: IEmbeddingProvider,
        vector_store: IVectorStoreProvider,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ) -> None:
        self._document_repo = document_repo
        self._chunk_repo = chunk_repo
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._extractor = TextExtractorDispatcher()
        self._chunker = TextChunker(chunk_size=chunk_size, overlap=chunk_overlap)
        self._enricher = MetadataEnricher()

    async def run(
        self,
        document: Document,
        progress_callback: ProgressCallback | None = None,
    ) -> int:
        doc_id = str(document.id)

        async def emit(stage: ProcessingStage, message: str, progress: int) -> None:
            if progress_callback:
                await progress_callback(doc_id, stage, message, progress)

        try:
            document.mark_processing()
            await self._document_repo.update(document)

            await emit(ProcessingStage.EXTRACTING, "Extracting text from document...", 20)
            raw_text = await self._extractor.extract(document.file_path)
            log.info("text_extracted", document_id=doc_id, chars=len(raw_text))

            await emit(ProcessingStage.CHUNKING, "Splitting into chunks...", 40)
            text_chunks = self._chunker.chunk(raw_text)
            log.info("chunks_created", document_id=doc_id, count=len(text_chunks))

            await emit(ProcessingStage.ENRICHING, "Extracting metadata...", 55)
            enriched_metadata = self._enricher.enrich(text_chunks, document.document_type.value)

            await emit(ProcessingStage.EMBEDDING, f"Generating embeddings for {len(text_chunks)} chunks...", 70)
            texts = [tc.text for tc in text_chunks]
            embeddings = await self._embedding_provider.encode_batch(texts)

            await emit(ProcessingStage.INDEXING, "Storing in vector index...", 88)

            chunks: list[Chunk] = []
            vector_records: list[dict] = []

            for i, (text_chunk, embedding, metadata) in enumerate(
                zip(text_chunks, embeddings, enriched_metadata)
            ):
                chunk_id = str(uuid.uuid4())
                chunk = Chunk(
                    id=uuid.UUID(chunk_id),
                    document_id=document.id,
                    chunk_index=i,
                    text=text_chunk.text,
                    embedding=embedding,
                    document_type=document.document_type.value,
                    metadata=metadata,
                )
                chunks.append(chunk)
                vector_records.append({
                    "chunk_id": chunk_id,
                    "document_id": doc_id,
                    "document_type": document.document_type.value,
                    "text": text_chunk.text,
                    "embedding": embedding,
                    "metadata": metadata,
                })

            await self._chunk_repo.save_batch(chunks)
            await self._vector_store.upsert_batch(vector_records)

            document.mark_completed(len(chunks))
            await self._document_repo.update(document)

            await emit(ProcessingStage.COMPLETED, f"Ready. {len(chunks)} chunks indexed.", 100)
            log.info("pipeline_completed", document_id=doc_id, chunks=len(chunks))
            return len(chunks)

        except Exception as exc:
            error_msg = str(exc)
            log.error("pipeline_failed", document_id=doc_id, error=error_msg)
            document.mark_failed(error_msg)
            await self._document_repo.update(document)
            await emit(ProcessingStage.FAILED, f"Processing failed: {error_msg}", 0)
            raise
