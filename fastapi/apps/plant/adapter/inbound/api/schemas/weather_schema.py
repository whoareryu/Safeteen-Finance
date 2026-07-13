from __future__ import annotations

from pydantic import BaseModel


class WeatherIngestRequest(BaseModel):
    region: str
    temp_c: float
    humidity_pct: float
    sunlight_desc: str


class WeatherSnapshotResponse(BaseModel):
    id: int
    region: str
    temp_c: float
    humidity_pct: float
    sunlight_desc: str
    is_dry_day: bool
