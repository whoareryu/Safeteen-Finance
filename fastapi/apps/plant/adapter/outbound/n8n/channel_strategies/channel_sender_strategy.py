from __future__ import annotations

from abc import ABC, abstractmethod


class ChannelSenderStrategy(ABC):
    """GoF Strategy — 알림 채널(카카오/디스코드/텔레그램)별 발송 방식을 캡슐화한다."""

    @abstractmethod
    async def send(self, message: str, coupang_link: str | None) -> None:
        pass
