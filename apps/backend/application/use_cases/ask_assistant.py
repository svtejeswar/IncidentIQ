from __future__ import annotations

from application.dto.assistant_dto import ChatRequest, ChatResponse
from application.services.ai_assistant_service import AIAssistantService


class AskAssistantUseCase:
    def __init__(self, assistant_service: AIAssistantService) -> None:
        self._service = assistant_service

    async def execute(self, request: ChatRequest) -> ChatResponse:
        return await self._service.chat(request)
