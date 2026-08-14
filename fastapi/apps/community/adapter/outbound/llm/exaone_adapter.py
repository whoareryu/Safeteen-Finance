from __future__ import annotations

from core.llm.ollama_chat_orchestrator import OllamaChatOrchestrator
from community.app.ports.output.llm_port import LlmPort


class ExaoneAdapter(LlmPort):
    def __init__(self, model: str = "exaone3.5:2.4b") -> None:
        self._llm = OllamaChatOrchestrator(model=model)

    async def chat(self, messages: list[dict]) -> str:
        return await self._llm.chat(messages)

    async def generate(self, prompt: str) -> str:
        return await self._llm.generate(prompt)
