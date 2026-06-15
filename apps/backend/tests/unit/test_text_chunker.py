"""Unit tests for the sliding-window text chunker."""
from __future__ import annotations

import pytest

from ingestion.chunkers.text_chunker import TextChunk, TextChunker


@pytest.fixture
def chunker() -> TextChunker:
    return TextChunker(chunk_size=10, overlap=2)


class TestTextChunkerEmptyInput:
    def test_empty_string_returns_no_chunks(self, chunker):
        assert chunker.chunk("") == []

    def test_whitespace_only_returns_no_chunks(self, chunker):
        assert chunker.chunk("   \n\t  ") == []


class TestTextChunkerSingleChunk:
    def test_short_text_produces_one_chunk(self, chunker):
        text = "word " * 5  # 5 words, well below chunk_size=10
        chunks = chunker.chunk(text)
        assert len(chunks) == 1

    def test_exact_chunk_size_produces_one_chunk(self, chunker):
        text = "word " * 10  # exactly chunk_size=10
        chunks = chunker.chunk(text)
        assert len(chunks) == 1

    def test_chunk_index_starts_at_zero(self, chunker):
        chunks = chunker.chunk("hello world")
        assert chunks[0].chunk_index == 0

    def test_chunk_contains_full_text(self, chunker):
        text = "hello world"
        chunks = chunker.chunk(text)
        assert chunks[0].text == "hello world"


class TestTextChunkerMultipleChunks:
    def test_long_text_produces_multiple_chunks(self, chunker):
        # 25 words with chunk_size=10 and overlap=2 should produce 3 chunks
        text = "word " * 25
        chunks = chunker.chunk(text)
        assert len(chunks) > 1

    def test_chunk_indices_are_sequential(self, chunker):
        text = "word " * 25
        chunks = chunker.chunk(text)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_chunks_have_correct_type(self, chunker):
        chunks = chunker.chunk("word " * 20)
        for chunk in chunks:
            assert isinstance(chunk, TextChunk)

    def test_overlap_means_adjacent_chunks_share_words(self, chunker):
        """With overlap=2, the last 2 words of chunk N appear in chunk N+1."""
        text = " ".join(f"w{i}" for i in range(25))
        chunks = chunker.chunk(text)
        if len(chunks) >= 2:
            last_words_of_first = chunks[0].text.split()[-2:]
            first_words_of_second = chunks[1].text.split()[:2]
            assert last_words_of_first == first_words_of_second

    def test_all_words_appear_in_at_least_one_chunk(self, chunker):
        words = [f"word{i}" for i in range(30)]
        text = " ".join(words)
        chunks = chunker.chunk(text)
        covered = set()
        for chunk in chunks:
            covered.update(chunk.text.split())
        for word in words:
            assert word in covered


class TestTextChunkerCleanup:
    def test_multiple_blank_lines_are_collapsed(self, chunker):
        text = "hello\n\n\n\nworld"
        chunks = chunker.chunk(text)
        combined = " ".join(c.text for c in chunks)
        assert "\n\n\n" not in combined

    def test_leading_trailing_whitespace_is_stripped(self, chunker):
        text = "   hello world   "
        chunks = chunker.chunk(text)
        assert chunks[0].text == "hello world"

    def test_multiple_spaces_are_collapsed(self, chunker):
        text = "hello    world"
        chunks = chunker.chunk(text)
        assert "  " not in chunks[0].text


class TestTextChunkerDefaults:
    def test_default_chunk_size_is_512(self):
        chunker = TextChunker()
        assert chunker._chunk_size == 512

    def test_default_overlap_is_50(self):
        chunker = TextChunker()
        assert chunker._overlap == 50

    def test_custom_chunk_size_is_respected(self):
        chunker = TextChunker(chunk_size=5, overlap=1)
        text = "word " * 20
        chunks = chunker.chunk(text)
        for chunk in chunks:
            assert len(chunk.text.split()) <= 5
