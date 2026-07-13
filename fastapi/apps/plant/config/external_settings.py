"""외부 API 키 — ``fastapi/.env``."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_ENV_PATH = _BACKEND_ROOT / ".env"


@dataclass(frozen=True)
class ExternalApiSettings:
    openweather_api_key: str
    openweather_city: str

    @property
    def openweather_configured(self) -> bool:
        return bool(self.openweather_api_key)


@lru_cache(maxsize=1)
def get_external_settings() -> ExternalApiSettings:
    load_dotenv(_ENV_PATH)
    return ExternalApiSettings(
        openweather_api_key=(os.getenv("OPENWEATHER_API_KEY") or "").strip(),
        openweather_city=(os.getenv("OPENWEATHER_CITY") or "Seoul").strip() or "Seoul",
    )
