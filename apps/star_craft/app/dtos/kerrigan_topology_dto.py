from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpokeInfo:
    name: str
    prefix: str
    status: str  # "active" | "inactive"


@dataclass(frozen=True)
class TopologyQuery:
    spoke_name: str | None = None


@dataclass(frozen=True)
class TopologyResponse:
    spokes: tuple[SpokeInfo, ...]
    total: int
