from __future__ import annotations

from abc import ABC, abstractmethod


class IFileStorage(ABC):
    @abstractmethod
    async def save(self, file_data: bytes, filename: str) -> str:
        """Save file and return the stored path."""
        ...

    @abstractmethod
    async def read(self, file_path: str) -> bytes: ...

    @abstractmethod
    async def delete(self, file_path: str) -> bool: ...

    @abstractmethod
    async def exists(self, file_path: str) -> bool: ...
