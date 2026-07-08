"""행정 구역 마스터 — district·sigungu_name 3NF 분리."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin

if TYPE_CHECKING:
    from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant


class SigunguDistrict(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "sigungu_districts"
    __table_args__ = (
        UniqueConstraint(
            "sigungu_name",
            "district_label",
            name="uq_sigungu_districts_name_label",
        ),
        Index("ix_sigungu_districts_district_label", "district_label"),
    )

    sigungu_name: Mapped[str] = mapped_column(String(32), default="", server_default="")
    district_label: Mapped[str] = mapped_column(String(128), default="", server_default="")

    restaurants: Mapped[list[Restaurant]] = relationship(back_populates="sigungu")
