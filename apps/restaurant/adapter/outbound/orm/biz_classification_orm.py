"""공공 업종 코드 마스터 — biz_mid/minor/ksic 3NF 분리."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin

if TYPE_CHECKING:
    from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant


class BizClassification(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "biz_classifications"
    __table_args__ = (
        UniqueConstraint(
            "biz_mid_name",
            "biz_minor_name",
            "ksic_name",
            name="uq_biz_classifications_triple",
        ),
        Index("ix_biz_classifications_ksic", "ksic_name"),
    )

    biz_mid_name: Mapped[str] = mapped_column(String(64), default="", server_default="")
    biz_minor_name: Mapped[str] = mapped_column(String(128), default="", server_default="")
    ksic_name: Mapped[str] = mapped_column(String(256), default="", server_default="")

    restaurants: Mapped[list[Restaurant]] = relationship(back_populates="biz_classification")
