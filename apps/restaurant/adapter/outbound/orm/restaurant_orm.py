"""GourmetMate 식당 엔티티 — 위치·업종·태그·연락은 FK 테이블 (1NF/2NF/3NF)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin
from restaurant.adapter.outbound.orm.gourmet_entity_orm import GourmetEntityMixin
from restaurant.app.use_cases.restaurant_location_interactor import distance_km_to_entity

if TYPE_CHECKING:
    from restaurant.adapter.outbound.orm.biz_classification_orm import BizClassification
    from restaurant.adapter.outbound.orm.food_category_orm import FoodCategory
    from restaurant.adapter.outbound.orm.restaurant_contact_orm import RestaurantContact
    from restaurant.adapter.outbound.orm.restaurant_menu_orm import RestaurantMenu
    from restaurant.adapter.outbound.orm.restaurant_operating_hour_orm import RestaurantOperatingHour
    from restaurant.adapter.outbound.orm.restaurant_price_orm import RestaurantPrice
    from restaurant.adapter.outbound.orm.restaurant_tag_orm import RestaurantTag
    from restaurant.adapter.outbound.orm.sigungu_district_orm import SigunguDistrict


class Restaurant(IntIdPrimaryKeyMixin, GourmetEntityMixin, Base):
    """넷플릭스형 브라우즈·식비 필터용 정제 식당."""

    __tablename__ = "restaurants"
    __table_args__ = (
        Index("ix_restaurants_category_sigungu_id", "category_id", "sigungu_id", "id"),
        Index("ix_restaurants_sigungu_id", "sigungu_id"),
        Index("ix_restaurants_biz_classification_id", "biz_classification_id"),
    )

    biz_number: Mapped[str] = mapped_column(String(48), unique=True, index=True)
    name: Mapped[str] = mapped_column(Text, index=True)
    store_name: Mapped[str] = mapped_column(Text, default="", server_default="")
    branch_name: Mapped[str] = mapped_column(Text, default="", server_default="")

    category_id: Mapped[int] = mapped_column(
        ForeignKey("food_categories.id", ondelete="RESTRICT"),
        index=True,
    )
    category: Mapped[FoodCategory] = relationship(back_populates="restaurants")

    sigungu_id: Mapped[int] = mapped_column(
        ForeignKey("sigungu_districts.id", ondelete="RESTRICT"),
        index=True,
    )
    sigungu: Mapped[SigunguDistrict] = relationship(back_populates="restaurants")

    biz_classification_id: Mapped[int] = mapped_column(
        ForeignKey("biz_classifications.id", ondelete="RESTRICT"),
        index=True,
    )
    biz_classification: Mapped[BizClassification] = relationship(
        back_populates="restaurants"
    )

    road_address: Mapped[str] = mapped_column(Text, default="", server_default="")
    parcel_address: Mapped[str] = mapped_column(Text, default="", server_default="")

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    image_url: Mapped[str] = mapped_column(String(512), default="", server_default="")

    view_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    price: Mapped[RestaurantPrice | None] = relationship(
        back_populates="restaurant",
        uselist=False,
        cascade="all, delete-orphan",
    )
    menus: Mapped[list[RestaurantMenu]] = relationship(
        back_populates="restaurant",
        cascade="all, delete-orphan",
        order_by="RestaurantMenu.sort_order",
    )
    tag_links: Mapped[list[RestaurantTag]] = relationship(
        back_populates="restaurant",
        cascade="all, delete-orphan",
    )
    contact: Mapped[RestaurantContact | None] = relationship(
        back_populates="restaurant",
        uselist=False,
        cascade="all, delete-orphan",
    )
    operating_hours: Mapped[list[RestaurantOperatingHour]] = relationship(
        back_populates="restaurant",
        cascade="all, delete-orphan",
        order_by="RestaurantOperatingHour.weekday",
    )

    @property
    def district(self) -> str:
        return (self.sigungu.district_label if self.sigungu else "") or ""

    @property
    def sigungu_name(self) -> str:
        return (self.sigungu.sigungu_name if self.sigungu else "") or ""

    @property
    def biz_mid_name(self) -> str:
        return (self.biz_classification.biz_mid_name if self.biz_classification else "") or ""

    @property
    def biz_minor_name(self) -> str:
        return (
            self.biz_classification.biz_minor_name if self.biz_classification else ""
        ) or ""

    @property
    def ksic_name(self) -> str:
        return (self.biz_classification.ksic_name if self.biz_classification else "") or ""

    @property
    def ai_tags(self) -> list[str]:
        labels: list[str] = []
        for link in self.tag_links or []:
            if link.tag and (link.tag.label or "").strip():
                labels.append(link.tag.label.strip())
        return labels

    @property
    def category_slug(self) -> str:
        return (self.category.slug if self.category else "") or "hansik"

    @property
    def category_label(self) -> str:
        return (self.category.label if self.category else "") or ""

    @property
    def avg_price(self) -> int | None:
        return self.price.avg_price if self.price is not None else None

    @property
    def signature_menu(self) -> str:
        for menu in self.menus or []:
            if menu.is_signature and (menu.name or "").strip():
                return menu.name.strip()
        for menu in self.menus or []:
            if (menu.name or "").strip():
                return menu.name.strip()
        return ""

    def display_name(self) -> str:
        return (self.name or "").strip() or "상호 미상"

    def category_pair(self) -> tuple[str, str]:
        slug = self.category_slug
        label = self.category_label
        if slug and label:
            return slug, label
        return slug or "hansik", label or slug

    def to_card_dict(
        self,
        *,
        user_lat: float | None = None,
        user_lng: float | None = None,
        rank: int | None = None,
        distance_km: float | None = None,
    ) -> dict[str, Any]:
        dist = distance_km
        if dist is None and user_lat is not None and user_lng is not None:
            dist = distance_km_to_entity(self, user_lat, user_lng)
        slug, label = self.category_pair()
        return {
            "id": self.id,
            "name": self.display_name(),
            "image_url": self.image_url or "",
            "district": self.district or "",
            "distance_km": dist,
            "rank": rank,
            "category_slug": slug,
            "category_label": label,
            "avg_price": self.avg_price,
            "signature_menu": self.signature_menu,
            "ai_tags": list(self.ai_tags),
        }

    def to_detail_dict(self) -> dict[str, Any]:
        slug, label = self.category_pair()
        addr = "\n".join(
            p for p in (self.road_address, self.parcel_address) if p
        ).strip()
        menu_items = [
            {
                "name": m.name,
                "price": m.unit_price,
                "is_signature": m.is_signature,
            }
            for m in (self.menus or [])
            if (m.name or "").strip()
        ]
        closed_days = [
            h.weekday for h in (self.operating_hours or []) if h.is_closed
        ]
        closed_label = (
            "연중무휴 (휴무 정보 없음)"
            if not closed_days
            else ", ".join(str(d) for d in sorted(closed_days))
        )
        hours_lines = [
            f"{h.weekday}:{h.open_time or ''}-{h.close_time or ''}"
            for h in (self.operating_hours or [])
            if not h.is_closed and (h.open_time or h.close_time)
        ]
        opening = (
            "; ".join(hours_lines)
            if hours_lines
            else "공공데이터에 영업 시간이 없습니다."
        )
        phone = self.contact.phone if self.contact else None
        place_url = self.contact.place_url if self.contact else None
        return {
            "id": self.id,
            "name": self.display_name(),
            "category_slug": slug,
            "category_label": label,
            "district": self.district or self.sigungu_name or "",
            "description": self.description or "",
            "image_url": self.image_url or "",
            "view_count": self.view_count,
            "closed_weekdays": closed_days,
            "closed_weekdays_label": closed_label,
            "address": addr,
            "opening_hours": opening,
            "phone": phone,
            "instagram_url": place_url,
            "reservation_available": False,
            "reservation_note": "",
            "menu_items": menu_items,
            "avg_price": self.avg_price,
            "signature_menu": self.signature_menu,
            "ai_tags": list(self.ai_tags),
            "road_address": self.road_address,
            "parcel_address": self.parcel_address,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }
