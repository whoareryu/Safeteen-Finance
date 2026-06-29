from __future__ import annotations

from sqlalchemy.orm import Session

from apps.auth.user_model import User
from user.app.dtos.visit_rating_dto import VisitConfirmCommand, VisitView
from user.app.ports.input.visit_rating_use_case import VisitRatingUseCase
from user.app.ports.output.visit_rating_repository import VisitRatingRepository


class VisitRatingInteractor(VisitRatingUseCase):
    def __init__(self, repository: VisitRatingRepository) -> None:
        self._repository = repository

    def confirm_visit(
        self, db: Session, user: User, command: VisitConfirmCommand
    ) -> VisitView:
        self._repository.add_visit(db, user_id=user.id, command=command)
        return VisitView(
            restaurant_id=command.restaurant_id,
            rating=command.rating,
            confirmed=True,
        )
