"""환경변수(.env) 시크릿 조회 전용 — LLM 등 다른 관심사와 분리."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(_BACKEND_DIR / ".env")

_REQUIRED = object()


class SecretManager:
    """.env 기반 시크릿 조회 — default 미지정 시 없으면 즉시 실패, 지정 시 폴백(None 포함)."""

    def get_secret(self, key: str, default: str | None = _REQUIRED) -> str | None:  # type: ignore[assignment]
        value = os.getenv(key)
        if value:
            return value
        if default is _REQUIRED:
            raise RuntimeError(f"{key}가 설정되지 않았습니다 (.env 확인).")
        return default


secret_manager = SecretManager()
