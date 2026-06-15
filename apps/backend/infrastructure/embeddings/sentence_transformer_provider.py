from __future__ import annotations

import asyncio
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from application.interfaces.embedding_provider import IEmbeddingProvider
from core.logging.logger import get_logger

log = get_logger(__name__)


class SentenceTransformerProvider(IEmbeddingProvider):
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._model: SentenceTransformer | None = None

    def _load_model(self) -> SentenceTransformer:
        if self._model is None:
            log.info("loading_embedding_model", model=self._model_name)
            self._model = SentenceTransformer(self._model_name)
        return self._model

    async def encode(self, text: str) -> list[float]:
        loop = asyncio.get_event_loop()
        model = self._load_model()
        embedding = await loop.run_in_executor(None, model.encode, text)
        return embedding.tolist()

    async def encode_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        loop = asyncio.get_event_loop()
        model = self._load_model()
        embeddings = await loop.run_in_executor(None, model.encode, texts)
        return [e.tolist() for e in embeddings]

    @property
    def dimensions(self) -> int:
        model = self._load_model()
        return model.get_sentence_embedding_dimension()
