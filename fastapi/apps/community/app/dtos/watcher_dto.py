from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class WatcherQuery:
    id: int
    name: str


@dataclass(frozen=True)
class WatcherResponse:
    id: int
    name: str


@dataclass(frozen=True)
class ClassifyCommand:
    text: str


@dataclass(frozen=True)
class ClassifyResult:
    violates: bool
    score: float
    matched: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    tokens: list[str] = field(default_factory=list)
