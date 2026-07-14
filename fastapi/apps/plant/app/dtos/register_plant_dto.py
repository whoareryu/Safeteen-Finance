from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterPlantCommand:
    owner_user_id: int | None
    region: str
    species_name: str | None
    photo_data: bytes | None = None
    photo_filename: str | None = None
    photo_content_type: str | None = None


@dataclass(frozen=True)
class RegisterPlantResult:
    id: int
    nickname: str
    species_name: str
    region: str
    growth_stage: str
    points: int
