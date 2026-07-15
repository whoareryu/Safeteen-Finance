from __future__ import annotations

from ontology.adapter.outbound.llm.qwen_intent_classifier_gateway import QwenIntentClassifierGateway
from ontology.app.ports.input.semantic_routing_use_case import SemanticRoutingUseCase
from ontology.app.use_cases.semantic_routing_interactor import SemanticRoutingInteractor
from ontology.dependencies.sommelier_graph_provider import get_sommelier_use_case
from ontology.dependencies.lens_search_provider import get_lens_use_case
from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator

# PoC 단계 + Qwen2.5-1.5B-Instruct 조건이라 QLoRA 파인튜닝 없이, 의도 분류
# 게이트웨이(라우팅용 프롬프트)와 RAG/일반 답변(답변용 프롬프트)에 같은
# 모델 하나(1.5B)를 나눠 쓴다. VRAM 8GB 환경에서 추가 GPU 메모리 소모 없이
# 구동 가능 — 실행 전 `ollama pull qwen2.5:1.5b-instruct` 필요.
_QWEN_MODEL = "qwen2.5:1.5b-instruct"


def get_semantic_routing_use_case() -> SemanticRoutingUseCase:
    return SemanticRoutingInteractor(
        llm=T1MidFakerOrchestrator(model=_QWEN_MODEL),
        intent_gateway=QwenIntentClassifierGateway(model=_QWEN_MODEL),
        sommelier=get_sommelier_use_case(),
        lens=get_lens_use_case(),
    )
