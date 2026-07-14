from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class CurrentWeatherData:
    region: str
    temp_c: float
    humidity_pct: float
    sunlight_desc: str


class WeatherApiGateway(ABC):
    """외부 날씨 API 출력 포트 — 실시간 현재 날씨 조회."""

    @abstractmethod
    async def fetch_current(self, region: str) -> CurrentWeatherData:
        pass
