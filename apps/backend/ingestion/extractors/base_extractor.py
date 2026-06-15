from __future__ import annotations

from abc import ABC, abstractmethod


class BaseExtractor(ABC):
    @abstractmethod
    async def extract(self, file_path: str) -> str:
        """Extract raw text from a file. Returns clean plain text."""
        ...

    @property
    @abstractmethod
    def supported_extensions(self) -> set[str]: ...
