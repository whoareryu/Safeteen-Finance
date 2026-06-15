import datetime

from sqlalchemy import Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin


class DailyPick(IntIdPrimaryKeyMixin, Base):
    """날짜별 오늘의 맛집 10선."""

    __tablename__ = "daily_picks"
    __table_args__ = (
        UniqueConstraint("pick_date", "restaurant_id", name="uq_daily_pick_date_restaurant"),
        UniqueConstraint("pick_date", "rank", name="uq_daily_pick_date_rank"),
    )

    pick_date: Mapped[datetime.date] = mapped_column(Date, index=True)
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurant.id", ondelete="CASCADE"), index=True
    )
    rank: Mapped[int] = mapped_column(Integer)

    restaurant: Mapped["Restaurant"] = relationship(  # noqa: F821
        "Restaurant"
    )
