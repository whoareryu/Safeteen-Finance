from __future__ import annotations

import asyncio

from ontology.app.ports.output.image_classifier_model_port import ImageClassifierModelPort

from plant.app.dtos.register_plant_dto import RegisterPlantCommand, RegisterPlantResult
from plant.app.ports.input.register_plant_use_case import RegisterPlantUseCase
from plant.app.ports.output.badge_repository import BadgeRepository
from plant.app.ports.output.llm_port import LlmPort
from plant.app.ports.output.plant_repository import PlantRepository
from plant.app.use_cases.diagnosis_interactor import _UNKNOWN_LABEL, _parse_label
from plant.domain.entities.plant_entity import PlantEntity

_NAMING_SYSTEM = (
    "당신은 반려식물에게 귀엽고 짧은 한국어 이름을 지어주는 작명가입니다. "
    "설명 없이 이름만 한 단어(또는 짧은 구)로 출력하세요. 따옴표나 마침표를 붙이지 마세요."
)


class RegisterPlantInteractor(RegisterPlantUseCase):

    def __init__(
        self,
        plant_repository: PlantRepository,
        badge_repository: BadgeRepository,
        llm: LlmPort,
        species_classifier: ImageClassifierModelPort,
    ) -> None:
        self._plant_repository = plant_repository
        self._badge_repository = badge_repository
        self._llm = llm
        self._species_classifier = species_classifier

    async def register(self, command: RegisterPlantCommand) -> RegisterPlantResult:
        species_name = command.species_name

        if command.photo_data is not None:
            prediction = await asyncio.to_thread(self._species_classifier.predict, command.photo_data)
            detected_species, _symptom = _parse_label(prediction.label or _UNKNOWN_LABEL)
            species_name = detected_species

        if not species_name:
            raise ValueError("species_name 또는 photo 중 하나는 반드시 필요합니다.")

        nickname = await self._generate_nickname(species_name, command.region)

        saved = await self._plant_repository.register(
            PlantEntity(
                id=None,
                owner_user_id=command.owner_user_id,
                nickname=nickname,
                species_name=species_name,
                region=command.region,
            )
        )
        await self._badge_repository.award_if_missing(saved.id, "first_register")  # type: ignore[arg-type]
        return RegisterPlantResult(
            id=saved.id,  # type: ignore[arg-type]
            nickname=saved.nickname,
            species_name=saved.species_name,
            region=saved.region,
            growth_stage=saved.growth_stage,
            points=saved.points,
        )

    async def _generate_nickname(self, species_name: str, region: str) -> str:
        prompt = f"종류: {species_name}, 키우는 장소: {region}. 이 식물의 귀여운 이름을 하나만 지어줘."
        try:
            reply = await self._llm.chat(
                [
                    {"role": "system", "content": _NAMING_SYSTEM},
                    {"role": "user", "content": prompt},
                ]
            )
            name = reply.strip().strip("\"'.,!?").splitlines()[0].strip()
            return name[:30] if name else species_name
        except Exception:
            return species_name
