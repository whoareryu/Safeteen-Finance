from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerPassengerData, JackTrainerQuery, JackTrainerResponse


class JackTrainerPort(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: JackTrainerQuery) -> JackTrainerResponse:
        pass

    @abstractmethod
    async def get_training_data(self) -> list[JackTrainerPassengerData]:
        pass
