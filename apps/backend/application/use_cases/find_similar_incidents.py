from __future__ import annotations

from uuid import UUID

from application.dto.search_dto import SimilarIncidentsResponse
from application.services.search_service import SearchService


class FindSimilarIncidentsUseCase:
    def __init__(self, search_service: SearchService) -> None:
        self._service = search_service

    async def execute(
        self,
        document_id: UUID | None = None,
        text: str | None = None,
        limit: int = 5,
    ) -> SimilarIncidentsResponse:
        return await self._service.find_similar(
            document_id=document_id,
            text=text,
            limit=limit,
        )
