from __future__ import annotations

import logging

import httpx

from plant.adapter.outbound.n8n.channel_strategies.channel_sender_strategy import (
    ChannelSenderStrategy,
)

logger = logging.getLogger(__name__)


class KakaoChannelStrategy(ChannelSenderStrategy):
    def __init__(self, webhook_url: str) -> None:
        self._url = webhook_url

    async def send(self, message: str, coupang_link: str | None) -> None:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    self._url,
                    json={"type": "kakao", "message": message, "coupang_link": coupang_link},
                )
                resp.raise_for_status()
        except Exception as e:
            logger.warning("n8n 카카오 알림 전송 실패: %s", e)
