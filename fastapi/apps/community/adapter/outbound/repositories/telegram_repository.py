from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from community.adapter.outbound.mappers.telegram_message_mapper import to_entity, to_orm
from community.adapter.outbound.orm.telegram_message_orm import TelegramMessageORM
from community.app.dtos.telegram_dto import TelegramQuery, TelegramResponse
from community.app.ports.output.telegram_port import TelegramPort
from community.domain.entities.telegram_message_entity import TelegramMessageEntity


class TelegramRepository(TelegramPort):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: TelegramQuery) -> TelegramResponse:
        return TelegramResponse(id=query.id, name=query.name)

    async def save_message(self, entity: TelegramMessageEntity) -> TelegramMessageEntity:
        orm = to_orm(entity)
        self.session.add(orm)
        await self.session.flush()
        return to_entity(orm)

    async def list_messages(self, limit: int) -> list[TelegramMessageEntity]:
        query = (
            select(TelegramMessageORM)
            .order_by(TelegramMessageORM.sent_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [to_entity(orm) for orm in result.scalars().all()]
