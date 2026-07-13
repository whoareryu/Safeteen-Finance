from __future__ import annotations

import logging

from plant.adapter.outbound.n8n.channel_strategies.channel_sender_strategy import (
    ChannelSenderStrategy,
)
from plant.app.dtos.notification_dto import NotificationSendDto
from plant.app.ports.output.notification_gateway import NotificationGateway

logger = logging.getLogger(__name__)


class N8nNotificationGateway(NotificationGateway):
    """채널별 발송 방식은 if/elif가 아니라 Strategy 레지스트리로 위임한다."""

    def __init__(self, strategies: dict[str, ChannelSenderStrategy]) -> None:
        self._strategies = strategies

    async def send(self, dto: NotificationSendDto) -> None:
        strategy = self._strategies.get(dto.channel)
        if strategy is None:
            logger.warning("등록되지 않은 알림 채널: %s", dto.channel)
            return
        await strategy.send(dto.message, dto.coupang_link)
