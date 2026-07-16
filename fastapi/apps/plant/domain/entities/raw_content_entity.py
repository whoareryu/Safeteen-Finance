from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RawContentEntity:
    url: str
    keyword: str
    title: str
    text: str
    extracted_at: str
