from __future__ import annotations

from plant.app.use_cases.notification_interactor import NotificationInteractor
from plant.domain.entities.care_schedule_entity import CareScheduleEntity
from plant.domain.entities.notification_event_entity import NotificationEventEntity
from plant.domain.entities.weather_snapshot_entity import WeatherSnapshotEntity


class _FakeCareScheduleRepository:
    def __init__(self, due: list[CareScheduleEntity]) -> None:
        self._due = due

    async def find_due(self, region: str):
        return self._due

    async def save(self, entity):
        raise NotImplementedError

    async def mark_watered(self, plant_id: int):
        raise NotImplementedError


class _FakeNotificationRepository:
    def __init__(self) -> None:
        self.saved: list[NotificationEventEntity] = []

    async def save(self, entity: NotificationEventEntity) -> NotificationEventEntity:
        saved = NotificationEventEntity(
            id=len(self.saved) + 1, plant_id=entity.plant_id, channel=entity.channel,
            message=entity.message, coupang_link=entity.coupang_link,
            triggered_by=entity.triggered_by, delivery_status="sent",
        )
        self.saved.append(saved)
        return saved

    async def find_by_plant(self, plant_id: int):
        return [n for n in self.saved if n.plant_id == plant_id]


class _FakeGateway:
    def __init__(self) -> None:
        self.sent: list[str] = []

    async def send(self, dto) -> None:
        self.sent.append(dto.channel)


class _FakeCoupangLink:
    def build_link(self, keyword: str) -> str:
        return f"https://coupang.example/{keyword}"


async def test_schedule_sends_and_records_single_notification():
    notification_repo = _FakeNotificationRepository()
    interactor = NotificationInteractor(
        care_schedule_repository=_FakeCareScheduleRepository(due=[]),
        notification_repository=notification_repo,
        gateway=_FakeGateway(),
        coupang_link=_FakeCoupangLink(),
    )

    result = await interactor.schedule(plant_id=7)

    assert result.plant_id == 7
    assert result.coupang_link == "https://coupang.example/식물 영양제"
    assert len(notification_repo.saved) == 1


async def test_dispatch_for_region_sends_for_every_due_schedule():
    due = [
        CareScheduleEntity(id=1, plant_id=10, interval_days=3, last_watered_at=None, next_watering_due_at=None),
        CareScheduleEntity(id=2, plant_id=11, interval_days=5, last_watered_at=None, next_watering_due_at=None),
    ]
    notification_repo = _FakeNotificationRepository()
    gateway = _FakeGateway()
    interactor = NotificationInteractor(
        care_schedule_repository=_FakeCareScheduleRepository(due=due),
        notification_repository=notification_repo,
        gateway=gateway,
        coupang_link=_FakeCoupangLink(),
    )
    snapshot = WeatherSnapshotEntity(
        id=1, region="서울", temp_c=30.0, humidity_pct=20.0, sunlight_desc="맑음", is_dry_day=True
    )

    results = await interactor.dispatch_for_region("서울", snapshot)

    assert len(results) == 2
    assert {r.plant_id for r in results} == {10, 11}
    assert gateway.sent == ["kakao", "kakao"]
