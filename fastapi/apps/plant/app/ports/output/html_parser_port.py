from __future__ import annotations

from abc import ABC, abstractmethod

from plant.domain.entities.raw_content_entity import RawContentEntity


class HtmlParserPort(ABC):
    """Outbound 출력 포트 — HTML 파싱. 링크 추출(크롤러)과 본문 추출(스크래퍼)에서 공유한다."""

    @abstractmethod
    def extract_links(self, html: str, base_url: str) -> list[str]:
        pass

    @abstractmethod
    def extract_content(self, html: str, url: str, keyword: str) -> RawContentEntity | None:
        """키워드가 본문에 없으면 None을 반환한다 (스크래퍼가 저장 여부를 판단하는 근거)."""
        pass
