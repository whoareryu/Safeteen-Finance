from __future__ import annotations

from abc import ABC, abstractmethod


class CrawlCommandInterpreterPort(ABC):
    """자연어 명령에서 크롤링/스크래핑에 필요한 (keyword, depth)를 추출한다."""

    @abstractmethod
    async def interpret(self, command: str) -> tuple[str, int]: ...
