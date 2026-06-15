from __future__ import annotations

from typing import AsyncGenerator

from groq import AsyncGroq

from application.interfaces.llm_provider import ILLMProvider, LLMMessage, LLMResponse
from core.logging.logger import get_logger

log = get_logger(__name__)


class GroqProvider(ILLMProvider):
    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float) -> None:
        self._client = AsyncGroq(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=temperature or self._temperature,
            max_tokens=max_tokens or self._max_tokens,
        )
        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            model=self._model,
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        stream = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=temperature or self._temperature,
            max_tokens=max_tokens or self._max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
