from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class TextChunk:
    text: str
    chunk_index: int
    start_char: int
    end_char: int


class TextChunker:
    """Sliding window chunker with sentence-aware splitting."""

    def __init__(self, chunk_size: int = 512, overlap: int = 50) -> None:
        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk(self, text: str) -> list[TextChunk]:
        text = self._clean(text)
        words = text.split()

        if not words:
            return []

        chunks: list[TextChunk] = []
        start = 0

        while start < len(words):
            end = min(start + self._chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            start_char = len(" ".join(words[:start]))
            end_char = start_char + len(chunk_text)

            chunks.append(
                TextChunk(
                    text=chunk_text,
                    chunk_index=len(chunks),
                    start_char=start_char,
                    end_char=end_char,
                )
            )

            if end >= len(words):
                break
            start = end - self._overlap

        return chunks

    def _clean(self, text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        return text.strip()
