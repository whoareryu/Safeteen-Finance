"""Repository 추상화 — DB 접근 은닉."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

TEntity = TypeVar("TEntity")


class AbstractRepository(ABC, Generic[TEntity]):
    """구체 Repository 가 상속 — ``Session`` 은 구현체 내부에서만 사용."""

    @abstractmethod
    def get_by_id(self, db: Session, entity_id: int) -> TEntity | None:
        raise NotImplementedError
