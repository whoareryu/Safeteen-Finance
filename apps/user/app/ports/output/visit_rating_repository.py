from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from user.app.dtos.visit_rating_dto import VisitConfirmCommand


class VisitRatingRepository(ABC):
    """restaurant_visits 영속화 포트."""

    @abstractmethod
    def add_visit(
        self, db: Session, *, user_id: int, command: VisitConfirmCommand
    ) -> None:
        ...
