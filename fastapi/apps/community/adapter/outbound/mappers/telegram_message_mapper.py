from __future__ import annotations

from community.adapter.outbound.orm.telegram_message_orm import TelegramMessageORM
from community.domain.entities.telegram_message_entity import TelegramMessageEntity


def to_entity(orm: TelegramMessageORM) -> TelegramMessageEntity:
    return TelegramMessageEntity(id=orm.id, text=orm.text, sent_at=orm.sent_at)


def to_orm(entity: TelegramMessageEntity) -> TelegramMessageORM:
    return TelegramMessageORM(text=entity.text, sent_at=entity.sent_at)
