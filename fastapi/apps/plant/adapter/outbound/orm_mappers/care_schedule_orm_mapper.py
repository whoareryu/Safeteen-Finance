from __future__ import annotations

from plant.adapter.outbound.orm.care_schedule_orm import CareScheduleORM
from plant.domain.entities.care_schedule_entity import CareScheduleEntity


def to_entity(orm: CareScheduleORM) -> CareScheduleEntity:
    return CareScheduleEntity(
        id=orm.id,
        plant_id=orm.plant_id,
        interval_days=orm.interval_days,
        last_watered_at=orm.last_watered_at,
        next_watering_due_at=orm.next_watering_due_at,
        status=orm.status,
    )


def to_orm(entity: CareScheduleEntity) -> CareScheduleORM:
    return CareScheduleORM(
        plant_id=entity.plant_id,
        interval_days=entity.interval_days,
        last_watered_at=entity.last_watered_at,
        next_watering_due_at=entity.next_watering_due_at,
        status=entity.status,
    )
