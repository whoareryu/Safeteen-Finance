from __future__ import annotations

from abc import ABC, abstractmethod


class LlmPort(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict]) -> str: ...

    @abstractmethod
    async def generate(self, prompt: str) -> str: ...
