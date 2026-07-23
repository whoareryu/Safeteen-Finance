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
from plant.domain.entities.diagnosis_record_entity import DiagnosisRecordEntity
from plant.domain.value_objects.plant_label_translator import (
    SYMPTOM_NOT_ASSESSED,
    translate_species,
    translate_symptom,
)

logger = logging.getLogger(__name__)

_BASE_SYSTEM = (
    "당신은 초보 식집사를 돕는 다정한 반려식물 케어 전문가입니다. "
    "진단된 품종과 증상을 바탕으로, 쉽고 따뜻한 말투의 한국어 케어 처방을 2~3문장으로 작성하세요. "
    "품종은 반드시 사용자가 알려준 이름 그대로만 언급하고, 다른 품종 이름을 지어내지 마세요."
)

# 이 값 미만이면 분류기 자체가 품종을 확신하지 못한다는 뜻이므로,
# LLM에게 확신에 찬 처방을 지어내게 하지 않고 재촬영을 안내한다.
# (symptom_confidence는 품종 전용 모델에서는 항상 0이 되므로 게이팅에 쓰지 않는다.)
_LOW_CONFIDENCE_THRESHOLD = 0.5
_LLM_TEMPERATURE = 0.3


def _low_confidence_message(species_ko: str, confidence: float) -> str:
    return (
        f"사진만으로는 {species_ko}가 맞는지 확신하기 어려워요(확신도 {confidence:.0%}). "
        "잎 전체가 잘 보이도록 밝은 곳에서 사진을 다시 찍어 올려주시면 더 정확하게 진단해 드릴게요!"
    )


def _fallback_prescription(species_ko: str, symptom_label: str) -> str:
    if symptom_label == SYMPTOM_NOT_ASSESSED:
        return (
            f"{species_ko}는 흙 표면이 마르면 물을 주고, "
            "직사광선을 피해 밝은 간접광에 두면 잘 자라요."
        )
    state = "건강해 보여요" if symptom_label == "healthy" else "조금 힘들어 보여요"
    return (
        f"{species_ko} 잎이 {state}. 흙 표면이 마르면 물을 주고, "
        "직사광선을 피해 밝은 간접광에 두면 좋아요."
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
        species_ko = translate_species(diagnosis.detected_species)

        if diagnosis.species_confidence < _LOW_CONFIDENCE_THRESHOLD:
            prescription_text = _low_confidence_message(species_ko, diagnosis.species_confidence)
        else:
            prescription_text = await self._generate_prescription(diagnosis, species_ko)

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

    async def _generate_prescription(self, diagnosis: DiagnosisRecordEntity, species_ko: str) -> str:
        system = await self._build_system(diagnosis.detected_species)
        system = f"{system}\n\n품종은 반드시 '{species_ko}'라는 이름으로만 언급하고, 다른 품종을 지어내지 마세요."

        if diagnosis.symptom_label == SYMPTOM_NOT_ASSESSED:
            system = (
                f"{system}\n\n증상 진단 기능은 아직 지원하지 않으니, 특정 병충해나 건강 상태를 "
                "단정하지 말고 이 품종을 키울 때 알아두면 좋은 기본 관리 팁만 안내하세요."
            )
            user_content = f"품종: {species_ko}. 이 품종의 기본 관리 팁을 알려주세요."
        else:
            symptom_ko = translate_symptom(diagnosis.symptom_label)
            user_content = (
                f"품종: {species_ko}, 증상: {symptom_ko} "
                f"(확신도 {diagnosis.symptom_confidence:.0%})"
            )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ]
        return await self._chat_until_species_matches(messages, species_ko, diagnosis.symptom_label)

    async def _chat_until_species_matches(
        self, messages: list[dict], species_ko: str, symptom_label: str
    ) -> str:
        text = await self._llm.chat(messages, temperature=_LLM_TEMPERATURE)
        if species_ko in text:
            return text

        logger.warning("케어 처방에 진단된 품종(%s)이 언급되지 않아 재생성 시도", species_ko)
        messages = [
            *messages,
            {"role": "assistant", "content": text},
            {
                "role": "user",
                "content": (
                    f"방금 답변에 '{species_ko}'라는 단어가 빠졌어요. "
                    f"'{species_ko}'을(를) 정확히 언급해서 다시 작성해 주세요."
                ),
            },
        ]
        retried = await self._llm.chat(messages, temperature=_LLM_TEMPERATURE)
        if species_ko in retried:
            return retried

        logger.warning("케어 처방 재생성에도 품종(%s) 불일치 — 기본 문구로 대체", species_ko)
        return _fallback_prescription(species_ko, symptom_label)

    async def _build_system(self, species: str) -> str:
        try:
            graph = await self._sommelier.query(
                GraphQueryDto(
                    cypher=(
                        "MATCH (s:Species) "
                        "WHERE toLower(s.name) CONTAINS toLower($species) "
                        "OR toLower($species) CONTAINS toLower(s.name) "
                        "RETURN s LIMIT 1"
                    ),
                    params={"species": species},
                )
            )
            facts = graph.records[0].get("s") if graph.records else None
            if facts:
                return f"{_BASE_SYSTEM}\n\n온톨로지 참고 사실:\n{facts}"
        except Exception:
            logger.warning("Sommelier 지식 그래프 조회 실패 — 기본 프롬프트로 진행")
        return _BASE_SYSTEM
