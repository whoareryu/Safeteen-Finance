from __future__ import annotations

from plant.app.dtos.weather_dto import WeatherIngestCommand
from plant.app.use_cases.weather_monitoring_interactor import WeatherMonitoringInteractor
from plant.domain.entities.weather_snapshot_entity import WeatherSnapshotEntity


class _FakeWeatherSnapshotRepository:
    def __init__(self) -> None:
        self.saved: WeatherSnapshotEntity | None = None

    async def save(self, entity: WeatherSnapshotEntity) -> WeatherSnapshotEntity:
        self.saved = WeatherSnapshotEntity(
            id=1, region=entity.region, temp_c=entity.temp_c,
            humidity_pct=entity.humidity_pct, sunlight_desc=entity.sunlight_desc,
            is_dry_day=entity.is_dry_day,
        )
        return self.saved

    async def find_latest(self, region: str):
        return self.saved


class _FakeNotificationUseCase:
    def __init__(self) -> None:
        self.dispatched_for: list[str] = []

    async def schedule(self, plant_id: int):
        raise NotImplementedError

    async def dispatch_for_region(self, region: str, snapshot):
        self.dispatched_for.append(region)
        return []


async def test_ingest_marks_dry_day_and_dispatches_notification():
    notification = _FakeNotificationUseCase()
    interactor = WeatherMonitoringInteractor(
        repository=_FakeWeatherSnapshotRepository(), notification=notification
    )

    result = await interactor.ingest(
        WeatherIngestCommand(region="서울", temp_c=28.0, humidity_pct=25.0, sunlight_desc="맑음")
    )

    assert result.is_dry_day is True
    assert notification.dispatched_for == ["서울"]


async def test_ingest_humid_day_does_not_dispatch_notification():
    notification = _FakeNotificationUseCase()
    interactor = WeatherMonitoringInteractor(
        repository=_FakeWeatherSnapshotRepository(), notification=notification
    )

    result = await interactor.ingest(
        WeatherIngestCommand(region="부산", temp_c=22.0, humidity_pct=70.0, sunlight_desc="흐림")
    )

    assert result.is_dry_day is False
    assert notification.dispatched_for == []
