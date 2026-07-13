from __future__ import annotations

from ontology.app.dtos.sommelier_dto import GraphResultDto

from plant.app.dtos.care_guide_dto import CareGuideCommand
from plant.app.use_cases.care_guide_interactor import CareGuideInteractor
from plant.domain.entities.care_prescription_entity import CarePrescriptionEntity
from plant.domain.entities.diagnosis_record_entity import DiagnosisRecordEntity


class _FakeDiagnosisRepository:
    async def save(self, entity):
        raise NotImplementedError

    async def get(self, diagnosis_id: int) -> DiagnosisRecordEntity:
        return DiagnosisRecordEntity(
            id=diagnosis_id, plant_id=1, photo_url="https://x/leaf.jpg",
            detected_species="monstera", species_confidence=0.9,
            symptom_label="overwatered_yellowing", symptom_confidence=0.9,
        )


class _FakeCarePrescriptionRepository:
    async def save(self, entity: CarePrescriptionEntity) -> CarePrescriptionEntity:
        return CarePrescriptionEntity(
            id=5, diagnosis_record_id=entity.diagnosis_record_id,
            prescription_text=entity.prescription_text, llm_model=entity.llm_model,
        )

    async def find_by_diagnosis(self, diagnosis_record_id: int):
        raise NotImplementedError


class _FakeLlm:
    async def chat(self, messages: list[dict]) -> str:
        return "지금 몬스테라 잎 끝이 노랗게 변하는 건 과습 때문이에요."

    async def generate(self, prompt: str) -> str:
        raise NotImplementedError


class _FakeSommelierUseCase:
    async def query(self, dto):
        return GraphResultDto(records=[{"humidity": "60-70%", "interval": 7}])


class _FailingSommelierUseCase:
    async def query(self, dto):
        raise RuntimeError("neo4j unavailable")


async def test_generate_returns_prescription_from_llm():
    interactor = CareGuideInteractor(
        diagnosis_repository=_FakeDiagnosisRepository(),
        care_prescription_repository=_FakeCarePrescriptionRepository(),
        llm=_FakeLlm(),
        sommelier=_FakeSommelierUseCase(),
    )

    result = await interactor.generate(CareGuideCommand(diagnosis_id=1))

    assert result.id == 5
    assert "과습" in result.prescription_text


async def test_generate_falls_back_when_sommelier_query_fails():
    interactor = CareGuideInteractor(
        diagnosis_repository=_FakeDiagnosisRepository(),
        care_prescription_repository=_FakeCarePrescriptionRepository(),
        llm=_FakeLlm(),
        sommelier=_FailingSommelierUseCase(),
    )

    result = await interactor.generate(CareGuideCommand(diagnosis_id=1))

    assert result.prescription_text
