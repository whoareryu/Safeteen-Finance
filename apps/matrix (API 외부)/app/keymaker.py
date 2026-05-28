"""시스템 전역 API 키·클라이언트 구성 (Gemini 등).

`backend/.env` 를 로드하고, 앱 어디서든 동일한 `keymaker` 인스턴스로 접근합니다.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class MissingGeminiKeyError(RuntimeError):
    """GEMINI_API_KEY 가 없거나 Gemini 클라이언트를 만들지 못한 경우."""


def _backend_env_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent / ".env"


# v1beta generateContent — `gemini-1.5-flash` 단독 ID는 404가 날 수 있음
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
MODEL_ALIASES: dict[str, str] = {
    "gemini-1.5-flash": "gemini-2.5-flash",
    "gemini-2.0-flash": "gemini-2.5-flash",
    "gemini-2.5-flash-preview-05-20": "gemini-2.5-flash",
}


class Keymaker:
    """전역 API 키 로딩 및 Gemini 클라이언트."""

    __slots__ = ("_gemini_api_key", "_gemini_model", "_gemini_model_name")

    def __init__(self, env_path: Optional[Path] = None) -> None:
        path = env_path if env_path is not None else _backend_env_path()
        load_dotenv(path)

        self._gemini_api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
        env_model = (os.getenv("GEMINI_MODEL") or "").strip()
        self._gemini_model_name = self.resolve_model_name(env_model or DEFAULT_GEMINI_MODEL)
        self._gemini_model: Optional[genai.GenerativeModel] = None

        if self._gemini_api_key:
            try:
                genai.configure(api_key=self._gemini_api_key)
                self._gemini_model = genai.GenerativeModel(self._gemini_model_name)
            except Exception:
                logger.exception("Keymaker: Gemini 초기화 실패")
                self._gemini_model = None
        else:
            logger.warning("Keymaker: GEMINI_API_KEY 없음 (/chat 등 비활성)")

    @staticmethod
    def resolve_model_name(name: str) -> str:
        trimmed = (name or "").strip()
        return MODEL_ALIASES.get(trimmed, trimmed) or DEFAULT_GEMINI_MODEL

    @property
    def gemini_model_name(self) -> str:
        return self._gemini_model_name

    @property
    def gemini_api_key_configured(self) -> bool:
        return bool(self._gemini_api_key) and self._gemini_model is not None

    def require_gemini_model(self) -> genai.GenerativeModel:
        if self._gemini_model is None:
            if not self._gemini_api_key:
                raise MissingGeminiKeyError(
                    "backend/.env 에 GEMINI_API_KEY 를 설정하세요.",
                )
            raise MissingGeminiKeyError(
                "Gemini 모델을 초기화할 수 없습니다. GEMINI_MODEL 또는 API 키를 확인하세요.",
            )
        return self._gemini_model

    def generative_model(self, model_name: str | None = None) -> genai.GenerativeModel:
        resolved = self.resolve_model_name(model_name or self._gemini_model_name)
        if resolved == self._gemini_model_name:
            return self.require_gemini_model()
        if not self._gemini_api_key:
            raise MissingGeminiKeyError(
                "backend/.env 에 GEMINI_API_KEY 를 설정하세요.",
            )
        genai.configure(api_key=self._gemini_api_key)
        return genai.GenerativeModel(resolved)


keymaker = Keymaker()
