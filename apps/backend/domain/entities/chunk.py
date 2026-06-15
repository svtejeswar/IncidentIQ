from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class Chunk:
    id: UUID
    document_id: UUID
    chunk_index: int
    text: str
    embedding: list[float]
    document_type: str
    metadata: dict = field(default_factory=dict)

    @property
    def has_embedding(self) -> bool:
        return len(self.embedding) > 0

    @property
    def word_count(self) -> int:
        return len(self.text.split())
