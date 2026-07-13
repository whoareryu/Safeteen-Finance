from __future__ import annotations

from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator
from community.app.ports.output.llm_port import LlmPort


class ExaoneAdapter(LlmPort):
    def __init__(self, model: str = "exaone3.5:2.4b") -> None:
        self._llm = T1MidFakerOrchestrator(model=model)

    async def chat(self, messages: list[dict]) -> str:
        return await self._llm.chat(messages)

    async def generate(self, prompt: str) -> str:
        return await self._llm.generate(prompt)
