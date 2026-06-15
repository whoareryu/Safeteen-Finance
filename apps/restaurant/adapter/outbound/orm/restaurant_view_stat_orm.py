import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin


class RestaurantViewStat(IntIdPrimaryKeyMixin, Base):
    """매장별 조회(관심) 횟수 — GourmetMate 관심도 지표."""

    __tablename__ = "restaurant_view_stats"

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurant.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    view_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    first_viewed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_viewed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    restaurant: Mapped["Restaurant"] = relationship(  # noqa: F821
        "Restaurant", back_populates="view_stat"
    )
