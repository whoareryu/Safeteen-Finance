"""외부 API 키 — ``fastapi/.env``."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from core.matrix.secret_manager import secret_manager


@dataclass(frozen=True)
class ExternalApiSettings:
    openweather_api_key: str
    openweather_city: str
    plant_air_purifying_api_key: str
    plant_drought_resistant_api_key: str
    plant_indoor_garden_api_key: str

    @property
    def openweather_configured(self) -> bool:
        return bool(self.openweather_api_key)

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
    return ExternalApiSettings(
        openweather_api_key=secret_manager.get_secret("OPENWEATHER_API_KEY", "").strip(),
        openweather_city=secret_manager.get_secret("OPENWEATHER_CITY", "Seoul").strip() or "Seoul",
        plant_air_purifying_api_key=secret_manager.get_secret("PLANT_AIR_PURIFYING_API_KEY", "").strip(),
        plant_drought_resistant_api_key=secret_manager.get_secret(
            "PLANT_DROUGHT_RESISTANT_API_KEY", ""
        ).strip(),
        plant_indoor_garden_api_key=secret_manager.get_secret("PLANT_INDOOR_GARDEN_API_KEY", "").strip(),
    )
