from __future__ import annotations

from sqlalchemy.orm import Session

from user.adapter.outbound.orm.restaurant_visit_orm import RestaurantVisit
from user.app.dtos.visit_rating_dto import VisitConfirmCommand
from user.app.ports.output.visit_rating_repository import VisitRatingRepository


class VisitRatingPgRepository(VisitRatingRepository):
    def add_visit(
        self, db: Session, *, user_id: int, command: VisitConfirmCommand
    ) -> None:
        db.add(
            RestaurantVisit(
                user_id=user_id,
                restaurant_id=command.restaurant_id,
                rating=command.rating,
                latitude=command.latitude,
                longitude=command.longitude,
            )
        )
        db.commit()
