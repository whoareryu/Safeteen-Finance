from __future__ import annotations

from restaurant.app.dtos.restaurant_domain_dto import RestaurantDomainQuery, RestaurantDomainResponse
from restaurant.app.ports.output.restaurant_domain_repository import RestaurantDomainRepository


class RestaurantDomainPgRepository(RestaurantDomainRepository):
    async def introduce_myself(self, query: RestaurantDomainQuery) -> RestaurantDomainResponse:
        return RestaurantDomainResponse(id=query.id, name=query.name)
