from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from apps.auth.user_model import User
from user.app.dtos.visit_rating_dto import VisitConfirmCommand, VisitView


class VisitRatingUseCase(ABC):
    """방문 확인 팝업 처리 + 별점 평가 (기획서 4-2)."""

    @abstractmethod
    def confirm_visit(
        self, db: Session, user: User, command: VisitConfirmCommand
    ) -> VisitView:
        ...
