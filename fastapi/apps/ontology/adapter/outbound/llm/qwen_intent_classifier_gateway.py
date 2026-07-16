from __future__ import annotations

import json

from ontology.app.dtos.intent_dto import IntentDto
from ontology.app.ports.output.intent_classification_gateway import IntentClassificationGateway
from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator

_QWEN_MODEL = "qwen2.5:1.5b-instruct"

_ROUTING_PROMPT = """너는 입력된 질문의 의도를 파악하는 분류 비서야.
아래 JSON 형식으로만 응답해. 설명·인사말 없이 JSON 한 덩어리만 출력해.

출력 스키마:
{"destination": "qwen_rag" | "gemini" | "crud", "entities": ["핵심 단어"]}

[분류 규칙 — 반드시 순서대로 확인]
1. 질문이 "등록해줘", "추가해줘", "삭제해줘", "수정해줘", "지워줘" 같은 명령형 동사로 데이터 생성·수정·삭제를 직접 요구하면 → "crud"
2. 그 외 식물 종류·품종·증상·병징·관리법·물주기·비료 등 식물 관리 지식이나 사내 전문 도메인 지식을 묻는 질문(있어?, 뭐야?, 왜?, 어떻게?, 알려줘 포함)은 전부 → "qwen_rag"
3. 식물·사내 지식과 무관한 일상 대화·인사·일반 상식 질문은 → "gemini"

주의: "물어보다", "알려줘", "어떻게 돼?" 같은 조회성 표현은 crud가 아니다. crud는 오직 규칙 1의 명령형 동사가 있을 때만 해당한다.

[예시]
질문: "회사 인프라 서버 사양이 어떻게 돼?"
답변: {"destination": "qwen_rag", "entities": ["인프라 서버", "사양"]}

질문: "사과잎에 생긴 검은 반점이 무슨 병인지 알려줘"
답변: {"destination": "qwen_rag", "entities": ["사과잎", "검은 반점"]}

질문: "잎이 노랗게 변했어, 왜 그럴까?"
답변: {"destination": "qwen_rag", "entities": ["잎", "노랗게 변함"]}

질문: "몬스테라 물 주기 주기가 어떻게 돼?"
답변: {"destination": "qwen_rag", "entities": ["몬스테라", "물 주기"]}

질문: "우리 식물 지식 DB에 Apple Scab Leaf 정보 있어?"
답변: {"destination": "qwen_rag", "entities": ["Apple Scab Leaf"]}

질문: "새로운 식물 하나 등록해줘"
답변: {"destination": "crud", "entities": ["식물 등록"]}

질문: "이 식물 기록 삭제해줘"
답변: {"destination": "crud", "entities": ["식물 기록 삭제"]}

질문: "오늘 점심 메뉴 뭐가 좋을까?"
답변: {"destination": "gemini", "entities": []}

질문: "안녕! 반가워"
답변: {"destination": "gemini", "entities": []}
"""

_CLASSIFY_TEMPERATURE = 0.1  # 라우팅 판단이 매번 흔들리지 않도록 낮은 온도로 고정


class QwenIntentClassifierGateway(IntentClassificationGateway):
    """PoC 단계 + Qwen2.5-1.5B-Instruct 조건에서는 QLoRA 파인튜닝 없이,
    라우팅 전용 시스템 프롬프트만 갈아 끼워 동일 모델로 의도를 분류한다."""

    def __init__(self, model: str = _QWEN_MODEL) -> None:
        self._llm = T1MidFakerOrchestrator(model=model)

    async def classify(self, question: str) -> IntentDto:
        routing_response = await self._llm.chat(
            [
                {"role": "system", "content": _ROUTING_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=_CLASSIFY_TEMPERATURE,
        )
        try:
            decision = json.loads(routing_response)
            return IntentDto(
                destination=decision.get("destination", "qwen_rag"),
                entities=decision.get("entities", []),
            )
        except (json.JSONDecodeError, AttributeError):
            return IntentDto(destination="qwen_rag", entities=[])
