from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.restaurant_domain_schema import RestaurantDomainSchema
from restaurant.app.dtos.restaurant_domain_dto import RestaurantDomainResponse


class RestaurantDomainUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: RestaurantDomainSchema) -> RestaurantDomainResponse:
        pass
