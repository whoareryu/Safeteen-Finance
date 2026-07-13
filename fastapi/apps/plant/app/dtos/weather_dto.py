from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WeatherIngestCommand:
    region: str
    temp_c: float
    humidity_pct: float
    sunlight_desc: str


@dataclass(frozen=True)
class WeatherSnapshotResult:
    id: int
    region: str
    temp_c: float
    humidity_pct: float
    sunlight_desc: str
    is_dry_day: bool
