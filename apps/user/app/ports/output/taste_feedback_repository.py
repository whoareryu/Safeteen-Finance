from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from user.app.dtos.taste_feedback_dto import FeedbackCommand


class TasteFeedbackRepository(ABC):
    """taste_feedbacks 영속화 포트."""

    @abstractmethod
    def add_signal(self, db: Session, *, user_id: int, command: FeedbackCommand) -> None:
        ...

    @abstractmethod
    def list_disliked_restaurant_ids(self, db: Session, user_id: int) -> list[int]:
        ...
