from __future__ import annotations

from plant.adapter.outbound.orm.weather_snapshot_orm import WeatherSnapshotORM
from plant.domain.entities.weather_snapshot_entity import WeatherSnapshotEntity


def to_entity(orm: WeatherSnapshotORM) -> WeatherSnapshotEntity:
    return WeatherSnapshotEntity(
        id=orm.id,
        region=orm.region,
        temp_c=orm.temp_c,
        humidity_pct=orm.humidity_pct,
        sunlight_desc=orm.sunlight_desc,
        is_dry_day=orm.is_dry_day,
        recorded_at=orm.recorded_at,
    )


def to_orm(entity: WeatherSnapshotEntity) -> WeatherSnapshotORM:
    return WeatherSnapshotORM(
        region=entity.region,
        temp_c=entity.temp_c,
        humidity_pct=entity.humidity_pct,
        sunlight_desc=entity.sunlight_desc,
        is_dry_day=entity.is_dry_day,
    )
