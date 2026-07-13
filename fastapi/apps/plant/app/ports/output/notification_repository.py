from __future__ import annotations

from abc import ABC, abstractmethod

from plant.domain.entities.notification_event_entity import NotificationEventEntity


class NotificationRepository(ABC):

    @abstractmethod
    async def save(self, entity: NotificationEventEntity) -> NotificationEventEntity:
        pass

    @abstractmethod
    async def find_by_plant(self, plant_id: int) -> list[NotificationEventEntity]:
        pass
