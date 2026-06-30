from __future__ import annotations

import logging

import httpx

from chef.app.dtos.email_dto import EmailTaskDto
from chef.app.ports.output.email_gateway import EmailGateway

logger = logging.getLogger(__name__)


class N8nEmailGateway(EmailGateway):
    def __init__(self, webhook_url: str) -> None:
        self._url = webhook_url

    async def send(self, dto: EmailTaskDto) -> None:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    self._url,
                    json={
                        "type": "email",
                        "to": dto.to,
                        "subject": dto.subject,
                        "body": dto.body,
                    },
                )
                resp.raise_for_status()
        except Exception as e:
            logger.warning("n8n 웹훅 전송 실패 (이메일 내용은 정상 생성됨): %s", e)
