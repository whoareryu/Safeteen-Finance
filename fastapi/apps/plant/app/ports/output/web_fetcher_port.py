from __future__ import annotations

from abc import ABC, abstractmethod


class WebFetcherPort(ABC):
    """Outbound 출력 포트 — 동기 HTML 페처.

    현재 구현체는 requests 기반(RequestsWebFetcher)이다. 동적 페이지 대응이
    필요해지면 이 포트를 구현하는 Selenium/Playwright 어댑터로 교체한다.
    """

    @abstractmethod
    def fetch(self, url: str) -> str:
        pass
