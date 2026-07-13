from __future__ import annotations

from plant.app.dtos.notification_dto import NotificationResult, NotificationSendDto
from plant.app.ports.input.notification_use_case import NotificationUseCase
from plant.app.ports.output.care_schedule_repository import CareScheduleRepository
from plant.app.ports.output.coupang_link_port import CoupangLinkPort
from plant.app.ports.output.notification_gateway import NotificationGateway
from plant.app.ports.output.notification_repository import NotificationRepository
from plant.domain.entities.notification_event_entity import NotificationEventEntity
from plant.domain.entities.weather_snapshot_entity import WeatherSnapshotEntity

_DEFAULT_CHANNEL = "kakao"
_NUTRIENT_KEYWORD = "식물 영양제"


def _build_message(nickname: str) -> str:
    return f"오늘 {nickname} 물 주는 날입니다! 건조한 날씨가 이어지고 있어요."


class NotificationInteractor(NotificationUseCase):

    def __init__(
        self,
        care_schedule_repository: CareScheduleRepository,
        notification_repository: NotificationRepository,
        gateway: NotificationGateway,
        coupang_link: CoupangLinkPort,
        channel: str = _DEFAULT_CHANNEL,
    ) -> None:
        self._care_schedule_repository = care_schedule_repository
        self._notification_repository = notification_repository
        self._gateway = gateway
        self._coupang_link = coupang_link
        self._channel = channel

    async def schedule(self, plant_id: int) -> NotificationResult:
        link = self._coupang_link.build_link(_NUTRIENT_KEYWORD)
        message = _build_message(f"식물 #{plant_id}")
        return await self._send_and_record(plant_id, message, link)

    async def dispatch_for_region(
        self, region: str, snapshot: WeatherSnapshotEntity
    ) -> list[NotificationResult]:
        due_schedules = await self._care_schedule_repository.find_due(region)
        link = self._coupang_link.build_link(_NUTRIENT_KEYWORD)

        results = []
        for due in due_schedules:
            message = _build_message(f"식물 #{due.plant_id}")
            results.append(await self._send_and_record(due.plant_id, message, link, triggered_by="dry_weather"))
        return results

    async def _send_and_record(
        self, plant_id: int, message: str, coupang_link: str, triggered_by: str = "schedule"
    ) -> NotificationResult:
        await self._gateway.send(
            NotificationSendDto(channel=self._channel, message=message, coupang_link=coupang_link)
        )
        saved = await self._notification_repository.save(
            NotificationEventEntity(
                id=None,
                plant_id=plant_id,
                channel=self._channel,
                message=message,
                coupang_link=coupang_link,
                triggered_by=triggered_by,
                delivery_status="sent",
            )
        )
        return NotificationResult(
            id=saved.id,  # type: ignore[arg-type]
            plant_id=saved.plant_id,
            channel=saved.channel,
            message=saved.message,
            coupang_link=saved.coupang_link,
            delivery_status=saved.delivery_status,
        )
