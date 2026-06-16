from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Any
from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerResponse


class JackTrainerUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/jack_trainer_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self,schema: list[JackTrainerSchema]) -> JackTrainerResponse:
        pass


    @abstractmethod
    async def train_model(self, train_set) -> dict[str, Any]:
        '''로즈가 제안한 모델들을 훈련시키는 메소드'''

