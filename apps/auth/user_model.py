from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.auth.user_role import UserRole
from apps.database import Base, IntIdPrimaryKeyMixin


class User(IntIdPrimaryKeyMixin, Base):
    """사이트 회원 — auth·secom 공통 단일 테이블 (`users`)."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            native_enum=False,
            # DB에는 "user"/"admin" (enum .value) 저장 — 이름 "USER"가 아님
            values_callable=lambda choices: [item.value for item in choices],
        ),
        default=UserRole.USER,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
