"""외부 API 키 — ``backend/.env`` (``apps/matrix`` Keymaker와 동일 루트)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

_BACKEND_ROOT = Path(__file__).resolve().parents[4]
_ENV_PATH = _BACKEND_ROOT / ".env"


@dataclass(frozen=True)
class ExternalApiSettings:
    kakao_rest_api_key: str
    localdata_api_key: str
    """공공데이터포털 활용신청 시 안내된 요청 URL (serviceKey 쿼리는 코드가 붙임)."""
    localdata_api_url: str
    localdata_base_url: str
    openweather_api_key: str
    openweather_city: str

    @property
    def kakao_configured(self) -> bool:
        return bool(self.kakao_rest_api_key)

    @property
    def localdata_configured(self) -> bool:
        return bool(self.localdata_api_key)

    @property
    def openweather_configured(self) -> bool:
        return bool(self.openweather_api_key)


@lru_cache(maxsize=1)
def get_external_settings() -> ExternalApiSettings:
    load_dotenv(_ENV_PATH)
    return ExternalApiSettings(
        kakao_rest_api_key=(os.getenv("KAKAO_REST_API_KEY") or "").strip(),
        localdata_api_key=(os.getenv("LOCALDATA_API_KEY") or "").strip(),
        localdata_api_url=(os.getenv("LOCALDATA_API_URL") or "").strip(),
        localdata_base_url=(
            os.getenv("LOCALDATA_BASE_URL")
            or "http://www.localdata.go.kr/platform/rest/GR0/openDataApi"
        ).strip(),
        openweather_api_key=(os.getenv("OPENWEATHER_API_KEY") or "").strip(),
        openweather_city=(os.getenv("OPENWEATHER_CITY") or "Seoul").strip() or "Seoul",
    )
