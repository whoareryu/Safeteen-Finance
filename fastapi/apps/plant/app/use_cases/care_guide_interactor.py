from __future__ import annotations

import logging

from ontology.app.dtos.sommelier_dto import GraphQueryDto
from ontology.app.ports.input.sommelier_graph_use_case import SommelierUseCase

from plant.app.dtos.care_guide_dto import CareGuideCommand, CareGuideResult
from plant.app.ports.input.care_guide_use_case import CareGuideUseCase
from plant.app.ports.output.care_prescription_repository import CarePrescriptionRepository
from plant.app.ports.output.diagnosis_repository import DiagnosisRepository
from plant.app.ports.output.llm_port import LlmPort
from plant.domain.entities.care_prescription_entity import CarePrescriptionEntity

logger = logging.getLogger(__name__)

_BASE_SYSTEM = (
    "당신은 초보 식집사를 돕는 다정한 반려식물 케어 전문가입니다. "
    "진단된 품종과 증상을 바탕으로, 쉽고 따뜻한 말투의 한국어 케어 처방을 2~3문장으로 작성하세요."
)


class CareGuideInteractor(CareGuideUseCase):

    def __init__(
        self,
        diagnosis_repository: DiagnosisRepository,
        care_prescription_repository: CarePrescriptionRepository,
        llm: LlmPort,
        sommelier: SommelierUseCase,
        llm_model_name: str = "exaone3.5:2.4b",
    ) -> None:
        self._diagnosis_repository = diagnosis_repository
        self._care_prescription_repository = care_prescription_repository
        self._llm = llm
        self._sommelier = sommelier
        self._llm_model_name = llm_model_name

    async def generate(self, command: CareGuideCommand) -> CareGuideResult:
        diagnosis = await self._diagnosis_repository.get(command.diagnosis_id)

        system = await self._build_system(diagnosis.detected_species, diagnosis.symptom_label)
        user_prompt = (
            f"품종: {diagnosis.detected_species}, 증상: {diagnosis.symptom_label} "
            f"(확신도 {diagnosis.symptom_confidence:.0%})"
        )
        prescription_text = await self._llm.chat(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ]
        )

        saved = await self._care_prescription_repository.save(
            CarePrescriptionEntity(
                id=None,
                diagnosis_record_id=diagnosis.id,  # type: ignore[arg-type]
                prescription_text=prescription_text.strip(),
                llm_model=self._llm_model_name,
            )
        )
        return CareGuideResult(
            id=saved.id,  # type: ignore[arg-type]
            diagnosis_record_id=saved.diagnosis_record_id,
            prescription_text=saved.prescription_text,
        )

    async def _build_system(self, species: str, symptom: str) -> str:
        try:
            graph = await self._sommelier.query(
                GraphQueryDto(
                    cypher=(
                        "MATCH (s:Species {name: $species})-[:HAS_SYMPTOM]->(d:Disease {name: $symptom}) "
                        "RETURN s.idealHumidity AS humidity, s.idealTemp AS temp, "
                        "s.wateringIntervalDays AS interval, d.description AS description"
                    ),
                    params={"species": species, "symptom": symptom},
                )
            )
            if graph.records:
                facts = graph.records[0]
                return f"{_BASE_SYSTEM}\n\n온톨로지 참고 사실:\n{facts}"
        except Exception:
            logger.warning("Sommelier 지식 그래프 조회 실패 — 기본 프롬프트로 진행")
        return _BASE_SYSTEM
