from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TargetUrlEntity:
    url: str
    keyword: str
    depth: int
