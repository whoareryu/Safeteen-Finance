from __future__ import annotations

from typing import Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.database import get_db
from ontology.adapter.outbound.llm.qwen_intent_classifier_gateway import QwenIntentClassifierGateway
from ontology.app.ports.input.semantic_routing_use_case import SemanticRoutingUseCase
from ontology.app.ports.output.plant_knowledge_search_port import PlantKnowledgeSearchPort
from ontology.app.use_cases.semantic_routing_interactor import SemanticRoutingInteractor
from ontology.dependencies.gemini_provider import get_gemini_use_case
from ontology.dependencies.sommelier_graph_provider import get_sommelier_use_case
from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator

# PoC 단계 + Qwen2.5-1.5B-Instruct 조건이라 QLoRA 파인튜닝 없이, 의도 분류
# 게이트웨이(라우팅용 프롬프트)와 RAG 답변(답변용 프롬프트)에 같은
# 모델 하나(1.5B)를 나눠 쓴다. VRAM 8GB 환경에서 추가 GPU 메모리 소모 없이
# 구동 가능 — 실행 전 `ollama pull qwen2.5:1.5b-instruct` 필요.
# "gemini" 분기는 로컬 모델이 아니라 실제 Gemini API(GeminiInteractor)로 답한다.
_QWEN_MODEL = "qwen2.5:1.5b-instruct"

# qwen_rag 분기의 실제 지식 소스는 plant 스포크의 pgvector(plant_knowledge)다.
# 허브(ontology)가 스포크(plant)를 직접 import할 수 없으므로, composition
# root(main.py)가 register_plant_knowledge_factory()로 구현체를 주입한다.
_plant_knowledge_factory: Callable[[AsyncSession], PlantKnowledgeSearchPort] | None = None


def register_plant_knowledge_factory(factory: Callable[[AsyncSession], PlantKnowledgeSearchPort]) -> None:
    global _plant_knowledge_factory
    _plant_knowledge_factory = factory


def get_semantic_routing_use_case(db: AsyncSession = Depends(get_db)) -> SemanticRoutingUseCase:
    if _plant_knowledge_factory is None:
        raise RuntimeError("plant_knowledge factory가 등록되지 않았습니다 (main.py 확인).")
    return SemanticRoutingInteractor(
        llm=T1MidFakerOrchestrator(model=_QWEN_MODEL),
        intent_gateway=QwenIntentClassifierGateway(model=_QWEN_MODEL),
        sommelier=get_sommelier_use_case(),
        plant_knowledge=_plant_knowledge_factory(db),
        gemini=get_gemini_use_case(),
    )
