from __future__ import annotations

from abc import ABC, abstractmethod


class MealPlanUseCase(ABC):
    @abstractmethod
    def get_current_plan(self, *args, **kwargs):
        pass

    @abstractmethod
    def upsert_plan(self, *args, **kwargs):
        pass

    @abstractmethod
    def remaining_budget(self, *args, **kwargs):
        pass

    @abstractmethod
    def restaurants_within_plan(self, *args, **kwargs):
        pass

    @abstractmethod
    async def introduce_myself(self, schema) -> "MealPlanIntroResponse":
        pass
