from __future__ import annotations

import re

from ingestion.chunkers.text_chunker import TextChunk

SEVERITY_PATTERNS = {
    "critical": re.compile(r"\b(critical|sev0|sev-0|p0|p-0|severity\s*0)\b", re.IGNORECASE),
    "high": re.compile(r"\b(high|sev1|sev-1|p1|p-1|severity\s*1)\b", re.IGNORECASE),
    "medium": re.compile(r"\b(medium|sev2|sev-2|p2|p-2|severity\s*2)\b", re.IGNORECASE),
    "low": re.compile(r"\b(low|sev3|sev-3|p3|p-3|severity\s*3)\b", re.IGNORECASE),
}

ROOT_CAUSE_PATTERNS = [
    re.compile(r"root\s+cause[:\s]+(.{20,200})", re.IGNORECASE),
    re.compile(r"caused\s+by[:\s]+(.{20,200})", re.IGNORECASE),
    re.compile(r"reason[:\s]+(.{20,200})", re.IGNORECASE),
]

RESOLUTION_PATTERNS = [
    re.compile(r"resolution[:\s]+(.{20,200})", re.IGNORECASE),
    re.compile(r"fixed\s+by[:\s]+(.{20,200})", re.IGNORECASE),
    re.compile(r"resolved\s+by[:\s]+(.{20,200})", re.IGNORECASE),
]

SERVICE_PATTERN = re.compile(
    r"\b([\w-]+-service|[\w-]+-api|[\w-]+-worker|[\w-]+-db|redis|postgres|mysql|kafka|sqs|sns|elasticsearch)\b",
    re.IGNORECASE,
)


class MetadataEnricher:
    def enrich(self, chunks: list[TextChunk], document_type: str) -> list[dict]:
        """Returns enriched metadata dict for each chunk."""
        return [self._enrich_chunk(chunk, document_type) for chunk in chunks]

    def _enrich_chunk(self, chunk: TextChunk, document_type: str) -> dict:
        text = chunk.text
        return {
            "chunk_index": chunk.chunk_index,
            "document_type": document_type,
            "severity": self._extract_severity(text),
            "affected_services": self._extract_services(text),
            "root_cause": self._extract_first_match(text, ROOT_CAUSE_PATTERNS),
            "resolution": self._extract_first_match(text, RESOLUTION_PATTERNS),
        }

    def _extract_severity(self, text: str) -> str:
        for level, pattern in SEVERITY_PATTERNS.items():
            if pattern.search(text):
                return level
        return "unknown"

    def _extract_services(self, text: str) -> list[str]:
        matches = SERVICE_PATTERN.findall(text)
        return list(dict.fromkeys(m.lower() for m in matches))[:10]

    def _extract_first_match(self, text: str, patterns: list[re.Pattern]) -> str | None:
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                return match.group(1).strip()[:200]
        return None
