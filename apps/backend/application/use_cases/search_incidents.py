from __future__ import annotations

from application.dto.search_dto import SearchRequest, SearchResponse
from application.services.search_service import SearchService


class SearchIncidentsUseCase:
    def __init__(self, search_service: SearchService) -> None:
        self._service = search_service

    async def execute(self, request: SearchRequest) -> SearchResponse:
        return await self._service.search(request)
