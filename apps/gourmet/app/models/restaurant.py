"""GourmetMate 식당 엔티티 — CSV·AI 메타 포함 (`restaurants`)."""

from __future__ import annotations

from sqlalchemy import Float, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class Restaurant(IntIdPrimaryKeyMixin, Base):
    """넷플릭스형 브라우즈·식비 필터용 정제 식당."""

    __tablename__ = "restaurants"
    __table_args__ = (
        Index("ix_restaurants_category_id", "category_slug", "id"),
        Index("ix_restaurants_category_district_id", "category_slug", "district", "id"),
        Index("ix_restaurants_category_price_id", "category_slug", "avg_price", "id"),
        Index("ix_restaurants_district", "district"),
    )

    biz_number: Mapped[str] = mapped_column(String(48), unique=True, index=True)
    name: Mapped[str] = mapped_column(Text, index=True)
    store_name: Mapped[str] = mapped_column(Text, default="", server_default="")
    branch_name: Mapped[str] = mapped_column(Text, default="", server_default="")

    category_slug: Mapped[str] = mapped_column(String(32), index=True)
    category_label: Mapped[str] = mapped_column(String(32), default="", server_default="")

    district: Mapped[str] = mapped_column(String(128), default="", server_default="")
    sigungu_name: Mapped[str] = mapped_column(String(32), default="", server_default="")
    road_address: Mapped[str] = mapped_column(Text, default="", server_default="")
    parcel_address: Mapped[str] = mapped_column(Text, default="", server_default="")

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    avg_price: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    signature_menu: Mapped[str] = mapped_column(String(256), default="", server_default="")
    ai_tags: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    image_url: Mapped[str] = mapped_column(String(512), default="", server_default="")

    biz_mid_name: Mapped[str] = mapped_column(String(64), default="", server_default="")
    biz_minor_name: Mapped[str] = mapped_column(String(128), default="", server_default="")
    ksic_name: Mapped[str] = mapped_column(String(256), default="", server_default="")

    view_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
