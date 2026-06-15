"""``restaurant_menus`` 조회."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.adapter.outbound.orm.restaurant_menu_orm import RestaurantMenu
from restaurant.app.ports.input.restaurant_menu_use_case import RestaurantMenuUseCase
from restaurant.adapter.inbound.api.schemas.restaurant_menu_schema import RestaurantMenuSchema
from restaurant.app.dtos.restaurant_menu_dto import RestaurantMenuQuery, RestaurantMenuResponse
from restaurant.app.ports.output.restaurant_menu_repository import RestaurantMenuRepository


def get_restaurant_menus(db: Session, restaurant_id: int) -> dict | None:
    if db.get(Restaurant, restaurant_id) is None:
        return None
    rows = db.scalars(
        select(RestaurantMenu)
        .where(RestaurantMenu.restaurant_id == restaurant_id)
        .order_by(
            RestaurantMenu.is_signature.desc(),
            RestaurantMenu.sort_order,
            RestaurantMenu.id,
        )
    ).all()
    menus = [
        {
            "id": m.id,
            "name": m.name,
            "is_signature": m.is_signature,
            "sort_order": m.sort_order,
            "unit_price": m.unit_price,
        }
        for m in rows
        if (m.name or "").strip()
    ]
    sig = next((m["name"] for m in menus if m["is_signature"]), "")
    if not sig and menus:
        sig = menus[0]["name"]
    return {
        "restaurant_id": restaurant_id,
        "menus": menus,
        "signature_menu": sig,
    }


class RestaurantMenuInteractor(RestaurantMenuUseCase):
    def __init__(self, repository: RestaurantMenuRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: RestaurantMenuSchema) -> RestaurantMenuResponse:
        return await self.repository.introduce_myself(
            RestaurantMenuQuery(id=schema.id, name=schema.name)
        )
