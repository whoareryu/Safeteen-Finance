from __future__ import annotations

from ontology.app.dtos.sommelier_dto import GraphResultDto

from plant.app.dtos.care_guide_dto import CareGuideCommand
from plant.app.use_cases.care_guide_interactor import CareGuideInteractor
from plant.domain.entities.care_prescription_entity import CarePrescriptionEntity
from plant.domain.entities.diagnosis_record_entity import DiagnosisRecordEntity


class _FakeDiagnosisRepository:
    def __init__(
        self, species="monstera_deliciosa_monstera_deliciosa", symptom="healthy", confidence=0.9, symptom_confidence=None,
    ) -> None:
        self._species = species
        self._symptom = symptom
        self._confidence = confidence
        self._symptom_confidence = confidence if symptom_confidence is None else symptom_confidence

    async def save(self, entity):
        raise NotImplementedError

    async def get(self, diagnosis_id: int) -> DiagnosisRecordEntity:
        return DiagnosisRecordEntity(
            id=diagnosis_id, plant_id=1, photo_url="https://x/leaf.jpg",
            detected_species=self._species, species_confidence=self._confidence,
            symptom_label=self._symptom, symptom_confidence=self._symptom_confidence,
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
    def __init__(self, reply: str) -> None:
        self._reply = reply
        self.calls: list[list[dict]] = []

    async def chat(self, messages: list[dict], temperature: float | None = None) -> str:
        self.calls.append(messages)
        return self._reply

    async def generate(self, prompt: str) -> str:
        raise NotImplementedError


class _ScriptedLlm:
    """호출마다 다른 응답을 순서대로 반환하는 페이크(재생성 흐름 테스트용)."""

    def __init__(self, replies: list[str]) -> None:
        self._replies = list(replies)
        self.calls: list[list[dict]] = []

    async def chat(self, messages: list[dict], temperature: float | None = None) -> str:
        self.calls.append(messages)
        return self._replies.pop(0)

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
        llm=_FakeLlm("지금 몬스테라 잎이 튼튼하게 잘 자라고 있어요."),
        sommelier=_FakeSommelierUseCase(),
    )

    result = await interactor.generate(CareGuideCommand(diagnosis_id=1))

    assert result.id == 5
    assert "몬스테라" in result.prescription_text


async def test_generate_falls_back_when_sommelier_query_fails():
    interactor = CareGuideInteractor(
        diagnosis_repository=_FakeDiagnosisRepository(),
        care_prescription_repository=_FakeCarePrescriptionRepository(),
        llm=_FakeLlm("몬스테라는 지금 상태가 좋아요."),
        sommelier=_FailingSommelierUseCase(),
    )

    result = await interactor.generate(CareGuideCommand(diagnosis_id=1))

    assert result.prescription_text


async def test_generate_retries_when_llm_names_wrong_species():
    llm = _ScriptedLlm([
        "딸기 품종이 잘 자라고 있어요.",
        "네, 몬스테라 잎이 건강하게 자라고 있어요.",
    ])
    interactor = CareGuideInteractor(
        diagnosis_repository=_FakeDiagnosisRepository(species="monstera_deliciosa_monstera_deliciosa"),
        care_prescription_repository=_FakeCarePrescriptionRepository(),
        llm=llm,
        sommelier=_FakeSommelierUseCase(),
    )

    result = await interactor.generate(CareGuideCommand(diagnosis_id=1))

    assert len(llm.calls) == 2
    assert "몬스테라" in result.prescription_text
    assert "딸기" not in result.prescription_text


async def test_generate_falls_back_to_template_when_species_still_wrong_after_retry():
    llm = _ScriptedLlm([
        "딸기 품종이 잘 자라고 있어요.",
        "딸기가 튼튼하게 자라고 있네요.",
    ])
    interactor = CareGuideInteractor(
        diagnosis_repository=_FakeDiagnosisRepository(species="monstera_deliciosa_monstera_deliciosa"),
        care_prescription_repository=_FakeCarePrescriptionRepository(),
        llm=llm,
        sommelier=_FakeSommelierUseCase(),
    )

    result = await interactor.generate(CareGuideCommand(diagnosis_id=1))

    assert len(llm.calls) == 2
    assert "몬스테라" in result.prescription_text
    assert "딸기" not in result.prescription_text


async def test_generate_returns_hedge_message_without_calling_llm_when_confidence_low():
    llm = _FakeLlm("이 문구는 호출되면 안 됩니다.")
    interactor = CareGuideInteractor(
        diagnosis_repository=_FakeDiagnosisRepository(species="monstera_deliciosa_monstera_deliciosa", confidence=0.37),
        care_prescription_repository=_FakeCarePrescriptionRepository(),
        llm=llm,
        sommelier=_FakeSommelierUseCase(),
    )

    result = await interactor.generate(CareGuideCommand(diagnosis_id=1))

    assert llm.calls == []
    assert "몬스테라" in result.prescription_text
    assert "37%" in result.prescription_text


async def test_generate_gives_general_tips_when_symptom_not_assessed():
    """품종 전용 모델(하우스플랜트 재학습분)은 symptom_confidence=0이지만,
    품종 자체는 확신도가 높으므로 헤징 없이 LLM을 호출해야 한다."""
    llm = _FakeLlm("몬스테라는 흙이 마르면 물을 주고 밝은 간접광에 두면 좋아요.")
    interactor = CareGuideInteractor(
        diagnosis_repository=_FakeDiagnosisRepository(
            species="monstera_deliciosa_monstera_deliciosa", symptom="not_assessed", confidence=0.9, symptom_confidence=0.0,
        ),
        care_prescription_repository=_FakeCarePrescriptionRepository(),
        llm=llm,
        sommelier=_FakeSommelierUseCase(),
    )

    result = await interactor.generate(CareGuideCommand(diagnosis_id=1))

    assert len(llm.calls) == 1
    user_message = llm.calls[0][-1]["content"]
    assert "증상" not in user_message
    assert "몬스테라" in result.prescription_text
