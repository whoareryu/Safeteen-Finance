from __future__ import annotations

import ollama


_MODEL = "exaone3.5:7.8b"


class T1MidFakerOrchestrator:
    """ExaOne 3.5:7.8b 로컬 모델 오케스트레이터."""

    def __init__(self, model: str = _MODEL) -> None:
        self._model = model
        self._client = ollama.AsyncClient()

    async def chat(self, messages: list[dict]) -> str:
        response = await self._client.chat(model=self._model, messages=messages)
        return response.message.content

    async def generate(self, prompt: str) -> str:
        response = await self._client.generate(model=self._model, prompt=prompt)
        return response.response
