from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class WeatherSnapshotEntity:
    id: int | None
    region: str
    temp_c: float
    humidity_pct: float
    sunlight_desc: str
    is_dry_day: bool
    recorded_at: datetime | None = None
