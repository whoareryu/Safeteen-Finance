"""``restaurant_menus`` 조회."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from gourmet.adapter.outbound.orm.restaurant import Restaurant
from gourmet.adapter.outbound.orm.restaurant_menu import RestaurantMenu


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
