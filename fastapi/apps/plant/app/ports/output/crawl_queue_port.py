from __future__ import annotations

from abc import ABC, abstractmethod

from plant.domain.entities.target_url_entity import TargetUrlEntity


class CrawlQueuePort(ABC):
    """Outbound 출력 포트 — Redis Hub의 작업 큐(Queue) + 중복 방지 필터(Visited Set)."""

    @abstractmethod
    async def push(self, target: TargetUrlEntity) -> None:
        pass

    @abstractmethod
    async def pop(self) -> TargetUrlEntity | None:
        pass

    @abstractmethod
    async def is_visited(self, url: str) -> bool:
        pass

    @abstractmethod
    async def mark_visited(self, url: str) -> None:
        pass
