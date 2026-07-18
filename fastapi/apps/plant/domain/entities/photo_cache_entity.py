from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PhotoCacheEntity:
    id: int | None
    species_name: str
    growth_stage: str
    status_key: str
    image_url: str
    pixabay_source_id: str
    fetched_at: datetime | None = None
