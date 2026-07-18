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
    plant_air_purifying_api_key: str
    plant_drought_resistant_api_key: str
    plant_indoor_garden_api_key: str
    pixabay_api_key: str

    @property
    def openweather_configured(self) -> bool:
        return bool(self.openweather_api_key)

    @property
    def pixabay_configured(self) -> bool:
        return bool(self.pixabay_api_key)

    @property
    def air_purifying_configured(self) -> bool:
        return bool(self.plant_air_purifying_api_key)

    @property
    def drought_resistant_configured(self) -> bool:
        return bool(self.plant_drought_resistant_api_key)

    @property
    def indoor_garden_configured(self) -> bool:
        return bool(self.plant_indoor_garden_api_key)


@lru_cache(maxsize=1)
def get_external_settings() -> ExternalApiSettings:
    load_dotenv(_ENV_PATH)
    return ExternalApiSettings(
        openweather_api_key=(os.getenv("OPENWEATHER_API_KEY") or "").strip(),
        openweather_city=(os.getenv("OPENWEATHER_CITY") or "Seoul").strip() or "Seoul",
        plant_air_purifying_api_key=(os.getenv("PLANT_AIR_PURIFYING_API_KEY") or "").strip(),
        plant_drought_resistant_api_key=(os.getenv("PLANT_DROUGHT_RESISTANT_API_KEY") or "").strip(),
        plant_indoor_garden_api_key=(os.getenv("PLANT_INDOOR_GARDEN_API_KEY") or "").strip(),
        pixabay_api_key=(os.getenv("PIXABAY_API_KEY") or "").strip(),
    )
