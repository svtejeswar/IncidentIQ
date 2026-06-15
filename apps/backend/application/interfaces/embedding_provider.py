from __future__ import annotations

from abc import ABC, abstractmethod


class IEmbeddingProvider(ABC):
    @abstractmethod
    async def encode(self, text: str) -> list[float]: ...

    @abstractmethod
    async def encode_batch(self, texts: list[str]) -> list[list[float]]: ...

    @property
    @abstractmethod
    def dimensions(self) -> int: ...
