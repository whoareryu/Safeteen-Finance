"""Gourmet 도메인 엔티티 추상화 — SQLAlchemy 와 ABC 메타클래스 충돌 방지."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class GourmetEntityProtocol(Protocol):
    """정적 타입용 계약 (다형성)."""

    id: int

    def display_name(self) -> str: ...
    def category_pair(self) -> tuple[str, str]: ...
    def to_card_dict(self, **kwargs: Any) -> dict[str, Any]: ...
    def to_detail_dict(self) -> dict[str, Any]: ...


class GourmetEntityMixin:
    """ORM 엔티티 믹스인 — 카드·상세 변환 캡슐화 (서브클래스가 구현)."""

    id: int

    def display_name(self) -> str:
        raise NotImplementedError

    def category_pair(self) -> tuple[str, str]:
        raise NotImplementedError

    def to_card_dict(
        self,
        *,
        user_lat: float | None = None,
        user_lng: float | None = None,
        rank: int | None = None,
        distance_km: float | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    def to_detail_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    @property
    def source_table(self) -> str:
        return self.__class__.__tablename__  # type: ignore[attr-defined]


class UserOwnedEntityMixin:
    """사용자 FK 엔티티 — 소유권 검사 은닉."""

    user_id: int

    def belongs_to_user(self, user_id: int) -> bool:
        return self.user_id == user_id
