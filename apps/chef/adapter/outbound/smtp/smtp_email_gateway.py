from __future__ import annotations

import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from chef.app.dtos.email_dto import EmailTaskDto
from chef.app.ports.output.email_gateway import EmailGateway

logger = logging.getLogger(__name__)

_HOST = "smtp.gmail.com"
_PORT = 587


class SmtpEmailGateway(EmailGateway):
    """Gmail SMTP를 통한 실제 이메일 전송 게이트웨이."""

    def __init__(self, smtp_user: str, smtp_password: str) -> None:
        self._user = smtp_user
        self._password = smtp_password

    async def send(self, dto: EmailTaskDto) -> None:
        await asyncio.to_thread(self._send_sync, dto)

    def _send_sync(self, dto: EmailTaskDto) -> None:
        msg = MIMEMultipart("alternative")
        msg["From"] = self._user
        msg["To"] = dto.to
        msg["Subject"] = dto.subject
        msg.attach(MIMEText(dto.body, "plain", "utf-8"))

        with smtplib.SMTP(_HOST, _PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(self._user, self._password)
            server.send_message(msg)
            logger.info("이메일 전송 완료 → %s", dto.to)
