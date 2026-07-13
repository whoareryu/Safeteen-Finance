from __future__ import annotations

from community.adapter.outbound.orm.receiver_orm import ReceiverORM
from community.domain.entities.receiver_entity import ReceiverEntity


class ReceiverMapper:
    @staticmethod
    def to_entity(orm: ReceiverORM) -> ReceiverEntity:
        return ReceiverEntity(
            id=orm.id,
            sender=orm.sender,
            recipient=orm.recipient,
            subject=orm.subject,
            preview=orm.preview,
            received_at=orm.received_at,
        )
