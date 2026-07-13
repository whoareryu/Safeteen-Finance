from __future__ import annotations

from abc import ABC, abstractmethod

from plant.app.dtos.notification_dto import NotificationSendDto


class NotificationGateway(ABC):
    @abstractmethod
    async def send(self, dto: NotificationSendDto) -> None: ...
