from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PixabayPhoto:
    source_id: str
    content_type: str
    data: bytes


class PixabayImageGateway(ABC):
    """외부 Pixabay API 출력 포트 — 검색어로 사진 1장을 찾아 다운로드까지 완료해 반환."""

    @abstractmethod
    async def fetch_photo(self, query: str) -> PixabayPhoto | None:
        pass
