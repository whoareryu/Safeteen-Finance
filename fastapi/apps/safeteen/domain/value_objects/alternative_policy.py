from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AlternativePolicy:
    """불법 대출 대신 안내할 합법 청년 금융 지원 정책 (예: 햇살론 유스)."""

    title: str
    description: str
    official_link: str
