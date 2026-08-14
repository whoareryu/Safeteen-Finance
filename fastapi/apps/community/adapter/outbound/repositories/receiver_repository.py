from __future__ import annotations

import logging

import ollama
from sqlalchemy.ext.asyncio import AsyncSession

from core.infra.secret_manager import secret_manager
from community.adapter.outbound.orm.receiver_orm import ReceiverORM
from community.app.dtos.receiver_dto import ReceiverCommand, ReceiverResult
from community.app.ports.output.receiver_port import ReceiverPort

logger = logging.getLogger(__name__)

_EMBED_MODEL = "bge-m3"


class ReceiverRepository(ReceiverPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, cmd: ReceiverCommand) -> ReceiverResult:
        embedding = await self._embed(f"{cmd.subject} {cmd.preview}")
        orm = ReceiverORM(
            sender=cmd.sender,
            recipient=cmd.recipient,
            subject=cmd.subject,
            preview=cmd.preview,
            message_id=cmd.message_id or None,
            embedding=embedding,
        )
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return ReceiverResult(
            id=orm.id,
            sender=orm.sender,
            subject=orm.subject,
            received_at=orm.received_at.isoformat(),
        )

    async def _embed(self, text: str) -> list[float] | None:
        try:
            client = ollama.AsyncClient(host=secret_manager.get_secret("OLLAMA_HOST", "http://localhost:11434"))
            resp = await client.embed(model=_EMBED_MODEL, input=text)
            return resp.embeddings[0]
        except Exception as e:
            logger.warning("[ReceiverRepository] 임베딩 실패, null 저장: %s", e)
            return None
