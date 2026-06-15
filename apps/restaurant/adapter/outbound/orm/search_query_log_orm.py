"""사용자 검색어 로그."""

from __future__ import annotations

import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class SearchQueryLog(IntIdPrimaryKeyMixin, Base):
    """GourmetMate 홈·검색창에서 실행된 검색어."""

    __tablename__ = "search_query_logs"

    query: Mapped[str] = mapped_column(String(128), index=True)
    query_normalized: Mapped[str] = mapped_column(String(128), index=True)
    result_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )
