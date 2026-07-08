from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from apps.auth.user_model import User
from user.app.dtos.taste_feedback_dto import FeedbackCommand


class TasteFeedbackUseCase(ABC):
    """'마음에 안 들어' 등 신호 기록 / 제외 식당 산출 (기획서 3-2, 4-1)."""

    @abstractmethod
    def record(self, db: Session, user: User, command: FeedbackCommand) -> None:
        ...

    @abstractmethod
    def excluded_restaurant_ids(self, db: Session, user_id: int) -> list[int]:
        ...
