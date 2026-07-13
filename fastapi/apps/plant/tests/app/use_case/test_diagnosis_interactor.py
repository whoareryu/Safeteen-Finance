from __future__ import annotations

from ontology.app.dtos.yolo_dto import YoloPredictResult

from plant.app.dtos.diagnosis_dto import DiagnosisUploadCommand
from plant.app.use_cases.diagnosis_interactor import DiagnosisInteractor
from plant.domain.entities.diagnosis_record_entity import DiagnosisRecordEntity
from plant.domain.entities.plant_entity import PlantEntity


class _FakePlantRepository:
    async def find_or_create(self, owner_user_id, region, species_hint) -> PlantEntity:
        return PlantEntity(
            id=1, owner_user_id=owner_user_id, nickname=species_hint,
            species_name=species_hint, region=region,
        )

    async def get(self, plant_id: int) -> PlantEntity:
        raise NotImplementedError


class _FakeDiagnosisRepository:
    def __init__(self) -> None:
        self.saved: DiagnosisRecordEntity | None = None

    async def save(self, entity: DiagnosisRecordEntity) -> DiagnosisRecordEntity:
        self.saved = DiagnosisRecordEntity(
            id=99,
            plant_id=entity.plant_id,
            photo_url=entity.photo_url,
            detected_species=entity.detected_species,
            species_confidence=entity.species_confidence,
            symptom_label=entity.symptom_label,
            symptom_confidence=entity.symptom_confidence,
        )
        return self.saved

    async def get(self, diagnosis_id: int) -> DiagnosisRecordEntity:
        assert self.saved is not None
        return self.saved


class _FakeYoloUseCase:
    def predict(self, command):
        return YoloPredictResult(name="monstera__overwatered_yellowing", confidence=0.92)

    def execute(self, command):
        raise NotImplementedError


class _FakeImageStorage:
    async def save(self, filename: str, content_type: str, data: bytes) -> str:
        return f"https://fake-bucket/{filename}"


async def test_diagnose_parses_species_and_symptom_from_label():
    interactor = DiagnosisInteractor(
        plant_repository=_FakePlantRepository(),
        diagnosis_repository=_FakeDiagnosisRepository(),
        yolo=_FakeYoloUseCase(),
        storage=_FakeImageStorage(),
    )

    result = await interactor.diagnose(
        DiagnosisUploadCommand(
            owner_user_id=1,
            region="서울",
            filename="leaf.jpg",
            content_type="image/jpeg",
            data=b"fake-bytes",
        )
    )

    assert result.detected_species == "monstera"
    assert result.symptom_label == "overwatered_yellowing"
    assert result.species_confidence == 0.92
    assert result.photo_url == "https://fake-bucket/leaf.jpg"


async def test_get_returns_previously_saved_diagnosis():
    diagnosis_repository = _FakeDiagnosisRepository()
    interactor = DiagnosisInteractor(
        plant_repository=_FakePlantRepository(),
        diagnosis_repository=diagnosis_repository,
        yolo=_FakeYoloUseCase(),
        storage=_FakeImageStorage(),
    )
    saved = await interactor.diagnose(
        DiagnosisUploadCommand(
            owner_user_id=None,
            region="부산",
            filename="a.jpg",
            content_type="image/jpeg",
            data=b"x",
        )
    )

    fetched = await interactor.get(saved.id)

    assert fetched.id == saved.id
    assert fetched.detected_species == saved.detected_species
