from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schema import CalTesterSchema
from titanic.app.dtos.passenger_cal_tester_dto import CalTesterResponse


class CalTesterUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/cal_tester_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self,schema: list[CalTesterSchema]) -> CalTesterResponse:
        pass
