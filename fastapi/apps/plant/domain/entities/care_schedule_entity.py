from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class CareScheduleEntity:
    id: int | None
    plant_id: int
    interval_days: int
    last_watered_at: datetime | None
    next_watering_due_at: datetime | None
    status: str = "active"
