"""시스템 전역 LLM 클라이언트 구성 (ExaOne via OllamaChatOrchestrator)."""

from __future__ import annotations

from core.llm.ollama_chat_orchestrator import OllamaChatOrchestrator
from core.infra.secret_manager import _REQUIRED, secret_manager


class GeminiCompatibleLocalLlmClient:
    """전역 LLM 클라이언트 — ExaOne 3.5:7.8b."""

    __slots__ = ("_orchestrator",)

    def __init__(self) -> None:
        self._orchestrator = OllamaChatOrchestrator()

    async def generate_content(self, contents: list[dict]) -> str:
        """Gemini 형식 contents를 ExaOne messages로 변환해 호출."""
        messages: list[dict] = []
        for item in contents:
            role = item.get("role", "user")
            parts = item.get("parts", [])
            text = " ".join(p.get("text", "") for p in parts if isinstance(p, dict))
            ollama_role = "assistant" if role == "model" else role
            messages.append({"role": ollama_role, "content": text})
        return await self._orchestrator.chat(messages)

    def get_secret(self, key: str, default: str | None = _REQUIRED) -> str | None:  # type: ignore[assignment]
        return secret_manager.get_secret(key, default)


gemini_compatible_local_llm_client = GeminiCompatibleLocalLlmClient()
