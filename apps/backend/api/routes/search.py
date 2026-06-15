from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.providers import get_search_use_case, get_similar_use_case
from application.dto.search_dto import (
    SearchRequest,
    SearchResponse,
    SimilarIncidentRequest,
    SimilarIncidentsResponse,
)
from application.use_cases.find_similar_incidents import FindSimilarIncidentsUseCase
from application.use_cases.search_incidents import SearchIncidentsUseCase
from domain.exceptions.domain_exceptions import SearchFailedException

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search_incidents(
    request: SearchRequest,
    use_case: Annotated[SearchIncidentsUseCase, Depends(get_search_use_case)],
) -> SearchResponse:
    try:
        return await use_case.execute(request)
    except SearchFailedException as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/similar", response_model=SimilarIncidentsResponse)
async def find_similar_incidents(
    request: SimilarIncidentRequest,
    use_case: Annotated[FindSimilarIncidentsUseCase, Depends(get_similar_use_case)],
) -> SimilarIncidentsResponse:
    if not request.document_id and not request.text:
        raise HTTPException(
            status_code=400,
            detail="Either document_id or text must be provided",
        )
    return await use_case.execute(
        document_id=request.document_id,
        text=request.text,
        limit=request.limit,
    )
