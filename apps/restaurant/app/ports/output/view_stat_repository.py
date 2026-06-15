from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.view_stat_dto import ViewStatQuery, ViewStatResponse


class ViewStatRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: ViewStatQuery) -> ViewStatResponse:
        pass
