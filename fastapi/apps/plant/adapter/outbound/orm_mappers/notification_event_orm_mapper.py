from __future__ import annotations

from plant.adapter.outbound.orm.notification_event_orm import NotificationEventORM
from plant.domain.entities.notification_event_entity import NotificationEventEntity


def to_entity(orm: NotificationEventORM) -> NotificationEventEntity:
    return NotificationEventEntity(
        id=orm.id,
        plant_id=orm.plant_id,
        channel=orm.channel,
        message=orm.message,
        coupang_link=orm.coupang_link,
        triggered_by=orm.triggered_by,
        delivery_status=orm.delivery_status,
        sent_at=orm.sent_at,
    )


def to_orm(entity: NotificationEventEntity) -> NotificationEventORM:
    return NotificationEventORM(
        plant_id=entity.plant_id,
        channel=entity.channel,
        message=entity.message,
        coupang_link=entity.coupang_link,
        triggered_by=entity.triggered_by,
        delivery_status=entity.delivery_status,
    )
