from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContextQuery:
    intent: str
    payload: str


@dataclass(frozen=True)
class ContextRouteResponse:
    target_spoke: str
    confidence: float
    reason: str
