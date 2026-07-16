from __future__ import annotations

import httpx

from community.app.ports.output.telegram_gateway import TelegramGateway


class TelegramBotGateway(TelegramGateway):
    """Telegram Bot API를 통한 실제 메시지 전송 게이트웨이 (n8n 미경유)."""

    def __init__(self, bot_token: str, chat_id: str) -> None:
        self._url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self._chat_id = chat_id

    async def send(self, text: str) -> None:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(self._url, json={"chat_id": self._chat_id, "text": text})
            resp.raise_for_status()
