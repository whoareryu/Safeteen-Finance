from __future__ import annotations

from pydantic import BaseModel, Field


class CourseStopResponse(BaseModel):
    slot: str
    restaurant_id: int
    name: str


class CourseResponse(BaseModel):
    district: str
    stops: list[CourseStopResponse] = Field(default_factory=list)
