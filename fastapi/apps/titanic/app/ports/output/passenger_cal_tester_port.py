from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_cal_tester_dto import CalTesterPassengerData, CalTesterQuery, CalTesterResponse


class CalTesterPort(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: CalTesterQuery) -> CalTesterResponse:
        pass

    @abstractmethod
    async def get_testing_data(self) -> list[CalTesterPassengerData]:
        pass
