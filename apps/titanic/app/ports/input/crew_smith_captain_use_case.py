from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import SmithCaptainSchema, ChatSchema
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainResponse, SmithChatResponse
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase


class SmithCaptainUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/smith_captain_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self, schema: list[SmithCaptainSchema]) -> SmithCaptainResponse:
        """Smith 선장 정보를 조회한다."""
        pass

    @abstractmethod
    async def chat(self, schema: ChatSchema,
                    jack: JackTrainerUseCase,
                    rose: RoseModelUseCase
                    ) -> SmithChatResponse:
        """사용자의 자연어 입력을 받아 응답한다."""
        pass
