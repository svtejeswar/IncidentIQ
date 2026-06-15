from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies.providers import get_assistant_use_case
from application.dto.assistant_dto import ChatRequest, ChatResponse
from application.use_cases.ask_assistant import AskAssistantUseCase

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    use_case: Annotated[AskAssistantUseCase, Depends(get_assistant_use_case)],
) -> ChatResponse:
    return await use_case.execute(request)
