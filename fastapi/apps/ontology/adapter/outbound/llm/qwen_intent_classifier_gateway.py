from __future__ import annotations

import json

from ontology.app.dtos.intent_dto import IntentDto
from ontology.app.ports.output.intent_classification_gateway import IntentClassificationGateway
from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator

_QWEN_MODEL = "qwen2.5:1.5b-instruct"

_ROUTING_PROMPT = """너는 입력된 질문의 의도를 파악하는 똑똑한 분류 비서야.
아래 지정된 JSON 형식으로만 응답해줘. 다른 친절한 설명이나 텍스트는 절대 붙이지 마.

출력 JSON 스키마:
{
  "destination": "crud" | "exaone_rag" | "gemini",
  "entities": ["질문 속 핵심 단어나 고유명사"]
}

[분류 기준]
- 사용자가 데이터 생성, 수정, 삭제를 명확히 요구할 때: "crud"
- 스타 토폴로지 내 노드 관계, 사내 전문 도메인 지식 질문: "exaone_rag"
- 일상 대화, 인사, 일반 상식 등 사내 정보가 필요 없는 질문: "gemini"

[예시]
질문: "회사 인프라 서버 사양이 어떻게 돼?"
답변: {"destination": "exaone_rag", "entities": ["인프라 서버", "사양"]}

질문: "사과잎에 생긴 검은 반점이 무슨 병인지 알려줘"
답변: {"destination": "exaone_rag", "entities": ["사과잎", "검은 반점"]}

질문: "우리 식물 지식 DB에 Apple Scab Leaf 정보 있어?"
답변: {"destination": "exaone_rag", "entities": ["Apple Scab Leaf"]}

질문: "새로운 식물 하나 등록해줘"
답변: {"destination": "crud", "entities": ["식물 등록"]}

질문: "오늘 점심 메뉴 뭐가 좋을까?"
답변: {"destination": "gemini", "entities": []}
"""


class QwenIntentClassifierGateway(IntentClassificationGateway):
    """PoC 단계 + Qwen2.5-1.5B-Instruct 조건에서는 QLoRA 파인튜닝 없이,
    라우팅 전용 시스템 프롬프트만 갈아 끼워 동일 모델로 의도를 분류한다."""

    def __init__(self, model: str = _QWEN_MODEL) -> None:
        self._llm = T1MidFakerOrchestrator(model=model)

    async def classify(self, question: str) -> IntentDto:
        routing_response = await self._llm.chat([
            {"role": "system", "content": _ROUTING_PROMPT},
            {"role": "user", "content": question},
        ])
        try:
            decision = json.loads(routing_response)
            return IntentDto(
                destination=decision.get("destination", "exaone_rag"),
                entities=decision.get("entities", []),
            )
        except (json.JSONDecodeError, AttributeError):
            return IntentDto(destination="exaone_rag", entities=[])
