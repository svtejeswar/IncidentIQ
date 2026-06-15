from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from application.services.ai_assistant_service import AIAssistantService
from application.services.document_service import DocumentService
from application.services.search_service import SearchService
from application.use_cases.ask_assistant import AskAssistantUseCase
from application.use_cases.find_similar_incidents import FindSimilarIncidentsUseCase
from application.use_cases.search_incidents import SearchIncidentsUseCase
from application.use_cases.upload_document import UploadDocumentUseCase
from core.config.settings import Settings, get_settings
from infrastructure.database.mongodb.client import get_database
from infrastructure.database.repositories.mongo_chunk_repository import MongoChunkRepository
from infrastructure.database.repositories.mongo_document_repository import MongoDocumentRepository
from infrastructure.database.repositories.mongo_incident_repository import MongoIncidentRepository
from infrastructure.embeddings.sentence_transformer_provider import SentenceTransformerProvider
from infrastructure.llm.groq.groq_provider import GroqProvider
from infrastructure.storage.local_storage import LocalFileStorage
from infrastructure.vector_store.mongodb_vector.mongo_vector_store import MongoVectorStore


def get_document_repo() -> MongoDocumentRepository:
    return MongoDocumentRepository(get_database())


def get_chunk_repo() -> MongoChunkRepository:
    return MongoChunkRepository(get_database())


def get_incident_repo() -> MongoIncidentRepository:
    return MongoIncidentRepository(get_database())


@lru_cache
def get_embedding_provider() -> SentenceTransformerProvider:
    settings = get_settings()
    return SentenceTransformerProvider(settings.embedding_model)


@lru_cache
def get_llm_provider() -> GroqProvider:
    settings = get_settings()
    return GroqProvider(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        max_tokens=settings.groq_max_tokens,
        temperature=settings.groq_temperature,
    )


def get_vector_store() -> MongoVectorStore:
    settings = get_settings()
    return MongoVectorStore(get_database(), settings.vector_index_name)


@lru_cache
def get_file_storage() -> LocalFileStorage:
    settings = get_settings()
    return LocalFileStorage(settings.upload_dir)


def get_document_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> DocumentService:
    return DocumentService(
        document_repo=get_document_repo(),
        chunk_repo=get_chunk_repo(),
        incident_repo=get_incident_repo(),
        file_storage=get_file_storage(),
        max_file_size_bytes=settings.max_file_size_bytes,
    )


def get_search_service() -> SearchService:
    return SearchService(
        embedding_provider=get_embedding_provider(),
        vector_store=get_vector_store(),
        llm_provider=get_llm_provider(),
        document_repo=get_document_repo(),
    )


def get_assistant_service() -> AIAssistantService:
    return AIAssistantService(
        embedding_provider=get_embedding_provider(),
        vector_store=get_vector_store(),
        llm_provider=get_llm_provider(),
        document_repo=get_document_repo(),
    )


def get_upload_use_case(
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> UploadDocumentUseCase:
    return UploadDocumentUseCase(service)


def get_search_use_case() -> SearchIncidentsUseCase:
    return SearchIncidentsUseCase(get_search_service())


def get_similar_use_case() -> FindSimilarIncidentsUseCase:
    return FindSimilarIncidentsUseCase(get_search_service())


def get_assistant_use_case() -> AskAssistantUseCase:
    return AskAssistantUseCase(get_assistant_service())
