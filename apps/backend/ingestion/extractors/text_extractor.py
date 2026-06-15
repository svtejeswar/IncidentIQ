from __future__ import annotations

import asyncio
from pathlib import Path

import aiofiles

from domain.exceptions.domain_exceptions import ExtractionFailedException
from ingestion.extractors.base_extractor import BaseExtractor


class PDFExtractor(BaseExtractor):
    @property
    def supported_extensions(self) -> set[str]:
        return {".pdf"}

    async def extract(self, file_path: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._extract_sync, file_path)

    def _extract_sync(self, file_path: str) -> str:
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n\n".join(p.strip() for p in pages if p.strip())
            if not text:
                raise ExtractionFailedException(file_path, "PDF contains no extractable text")
            return text
        except ExtractionFailedException:
            raise
        except Exception as e:
            raise ExtractionFailedException(file_path, str(e)) from e


class DocxExtractor(BaseExtractor):
    @property
    def supported_extensions(self) -> set[str]:
        return {".docx"}

    async def extract(self, file_path: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._extract_sync, file_path)

    def _extract_sync(self, file_path: str) -> str:
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(file_path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            text = "\n\n".join(paragraphs)
            if not text:
                raise ExtractionFailedException(file_path, "DOCX contains no text")
            return text
        except ExtractionFailedException:
            raise
        except Exception as e:
            raise ExtractionFailedException(file_path, str(e)) from e


class PlainTextExtractor(BaseExtractor):
    @property
    def supported_extensions(self) -> set[str]:
        return {".txt", ".md"}

    async def extract(self, file_path: str) -> str:
        try:
            async with aiofiles.open(file_path, encoding="utf-8", errors="ignore") as f:
                text = await f.read()
            if not text.strip():
                raise ExtractionFailedException(file_path, "File is empty")
            return text
        except ExtractionFailedException:
            raise
        except Exception as e:
            raise ExtractionFailedException(file_path, str(e)) from e


class TextExtractorDispatcher:
    """Routes files to the correct extractor based on file extension."""

    def __init__(self) -> None:
        self._extractors: dict[str, BaseExtractor] = {}
        for extractor in [PDFExtractor(), DocxExtractor(), PlainTextExtractor()]:
            for ext in extractor.supported_extensions:
                self._extractors[ext] = extractor

    async def extract(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        extractor = self._extractors.get(ext)
        if not extractor:
            raise ExtractionFailedException(file_path, f"No extractor for extension: {ext}")
        return await extractor.extract(file_path)
