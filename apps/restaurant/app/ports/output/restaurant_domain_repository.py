from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.restaurant_domain_dto import RestaurantDomainQuery, RestaurantDomainResponse


class RestaurantDomainRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: RestaurantDomainQuery) -> RestaurantDomainResponse:
        pass
