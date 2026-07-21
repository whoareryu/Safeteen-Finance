from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from ontology.app.ports.output.image_classifier_model_port import ImageClassifierModelPort
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway

from plant.app.dtos.checkin_dto import CheckinCommand, CheckinResult
from plant.app.ports.input.checkin_use_case import CheckinUseCase
from plant.app.ports.output.badge_repository import BadgeRepository
from plant.app.ports.output.care_schedule_repository import CareScheduleRepository
from plant.app.ports.output.plant_checkin_repository import PlantCheckinRepository
from plant.app.ports.output.plant_repository import PlantRepository
from plant.app.use_cases.diagnosis_interactor import _UNKNOWN_LABEL, _parse_label
from plant.domain.entities.plant_checkin_entity import PlantCheckinEntity
from plant.domain.value_objects.growth_stage import MATURE, NEW_SHOOT, compute_growth_stage

_BASE_POINTS = 10
_STREAK_7_BONUS = 50
_STREAK_30_BONUS = 200
_CARE_SCHEDULE_BONUS = 5


class CheckinInteractor(CheckinUseCase):

    def __init__(
        self,
        plant_repository: PlantRepository,
        checkin_repository: PlantCheckinRepository,
        badge_repository: BadgeRepository,
        care_schedule_repository: CareScheduleRepository,
        species_classifier: ImageClassifierModelPort,
        storage: ImageStorageGateway,
    ) -> None:
        self._plant_repository = plant_repository
        self._checkin_repository = checkin_repository
        self._badge_repository = badge_repository
        self._care_schedule_repository = care_schedule_repository
        self._species_classifier = species_classifier
        self._storage = storage

    async def checkin(self, command: CheckinCommand) -> CheckinResult:
        plant = await self._plant_repository.get(command.plant_id)
        today = datetime.now(timezone.utc).date()

        if plant.last_checkin_date == today:
            raise ValueError("오늘은 이미 출석체크를 완료했습니다.")

        photo_url = await self._storage.save(
            command.photo_filename, command.photo_content_type, command.photo_data
        )

        prediction = await asyncio.to_thread(self._species_classifier.predict, command.photo_data)
        _species, symptom = _parse_label(prediction.label or _UNKNOWN_LABEL)
        health_score = (
            100.0 if symptom == "healthy" else round(100 - prediction.confidence * 60, 1)
        )

        if plant.last_checkin_date is not None and (today - plant.last_checkin_date).days == 1:
            new_streak = plant.streak_count + 1
        else:
            new_streak = 1

        points_earned = _BASE_POINTS + round(health_score / 10)

        schedule = await self._care_schedule_repository.get_by_plant(plant.id)  # type: ignore[arg-type]
        if (
            schedule is not None
            and schedule.next_watering_due_at is not None
            and schedule.next_watering_due_at.date() <= today
        ):
            points_earned += _CARE_SCHEDULE_BONUS

        if new_streak == 7:
            points_earned += _STREAK_7_BONUS
        elif new_streak == 30:
            points_earned += _STREAK_30_BONUS

        new_points = plant.points + points_earned
        old_stage = plant.growth_stage
        new_stage = compute_growth_stage(new_points)

        checkin_count_before = await self._checkin_repository.count_by_plant(plant.id)  # type: ignore[arg-type]

        saved_checkin = await self._checkin_repository.save(
            PlantCheckinEntity(
                id=None,
                plant_id=plant.id,  # type: ignore[arg-type]
                photo_url=photo_url,
                checkin_date=today,
                health_score=health_score,
                points_earned=points_earned,
                streak_day=new_streak,
            )
        )

        plant.points = new_points
        plant.streak_count = new_streak
        plant.growth_stage = new_stage
        plant.last_checkin_date = today
        await self._plant_repository.update(plant)

        new_badges: list[str] = []
        if checkin_count_before == 0:
            if await self._badge_repository.award_if_missing(plant.id, "first_checkin"):  # type: ignore[arg-type]
                new_badges.append("first_checkin")
        if new_streak == 7:
            if await self._badge_repository.award_if_missing(plant.id, "streak_7"):  # type: ignore[arg-type]
                new_badges.append("streak_7")
        if new_streak == 30:
            if await self._badge_repository.award_if_missing(plant.id, "streak_30"):  # type: ignore[arg-type]
                new_badges.append("streak_30")
        if old_stage != NEW_SHOOT and new_stage == NEW_SHOOT:
            if await self._badge_repository.award_if_missing(plant.id, "growth_new_shoot"):  # type: ignore[arg-type]
                new_badges.append("growth_new_shoot")
        if old_stage != MATURE and new_stage == MATURE:
            if await self._badge_repository.award_if_missing(plant.id, "growth_mature"):  # type: ignore[arg-type]
                new_badges.append("growth_mature")

        return CheckinResult(
            id=saved_checkin.id,  # type: ignore[arg-type]
            plant_id=plant.id,  # type: ignore[arg-type]
            checkin_date=today,
            health_score=health_score,
            points_earned=points_earned,
            streak_day=new_streak,
            total_points=new_points,
            growth_stage=new_stage,
            new_badges=new_badges,
        )
