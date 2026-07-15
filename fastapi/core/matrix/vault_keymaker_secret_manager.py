"""시스템 전역 LLM 클라이언트 구성 (ExaOne via T1MidFakerOrchestrator)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator


def _backend_env_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / ".env"


load_dotenv(_backend_env_path())


class Keymaker:
    """전역 LLM 클라이언트 — ExaOne 3.5:7.8b — 겸 .env 시크릿 접근점."""

    __slots__ = ("_faker",)

    def __init__(self) -> None:
        self._faker = T1MidFakerOrchestrator()

    async def generate_content(self, contents: list[dict]) -> str:
        """Gemini 형식 contents를 ExaOne messages로 변환해 호출."""
        messages: list[dict] = []
        for item in contents:
            role = item.get("role", "user")
            parts = item.get("parts", [])
            text = " ".join(p.get("text", "") for p in parts if isinstance(p, dict))
            ollama_role = "assistant" if role == "model" else role
            messages.append({"role": ollama_role, "content": text})
        return await self._faker.chat(messages)

    def get_secret(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise RuntimeError(f"{key}가 설정되지 않았습니다 (.env 확인).")
        return value


keymaker = Keymaker()
