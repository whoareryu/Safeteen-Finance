from __future__ import annotations

from plant.adapter.inbound.api.schemas.checkin_schema import CheckinResponse
from plant.app.dtos.checkin_dto import CheckinResult


def to_response(result: CheckinResult) -> CheckinResponse:
    return CheckinResponse(
        id=result.id,
        plant_id=result.plant_id,
        checkin_date=result.checkin_date,
        health_score=result.health_score,
        points_earned=result.points_earned,
        streak_day=result.streak_day,
        total_points=result.total_points,
        growth_stage=result.growth_stage,
        new_badges=result.new_badges,
    )
