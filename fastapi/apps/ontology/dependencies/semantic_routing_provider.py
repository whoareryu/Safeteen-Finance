from __future__ import annotations

from ontology.adapter.outbound.llm.gemini_langchain_chatbot_gateway import GeminiLangchainChatbotGateway
from ontology.adapter.outbound.llm.exaone_intent_classifier_gateway import ExaoneIntentClassifierGateway
from ontology.app.ports.input.semantic_routing_use_case import SemanticRoutingUseCase
from ontology.app.use_cases.semantic_routing_interactor import SemanticRoutingInteractor
from ontology.dependencies.sommelier_graph_provider import get_sommelier_use_case
from core.llm.ollama_chat_orchestrator import OllamaChatOrchestrator

# PoC 단계 + EXAONE 3.5 2.4B 조건이라 QLoRA 파인튜닝 없이, 의도 분류
# 게이트웨이(라우팅용 프롬프트)와 RAG 답변(답변용 프롬프트)에 같은
# 모델 하나(2.4B)를 나눠 쓴다. VRAM 8GB 환경에서 추가 GPU 메모리 소모 없이
# 구동 가능 — 실행 전 `ollama pull exaone3.5:2.4b` 필요.
# "gemini" 분기는 LangChain + 실제 Gemini(GeminiLangchainChatbotGateway)로 답한다.
_EXAONE_MODEL = "exaone3.5:2.4b"


def get_semantic_routing_use_case() -> SemanticRoutingUseCase:
    return SemanticRoutingInteractor(
        llm=OllamaChatOrchestrator(model=_EXAONE_MODEL),
        intent_gateway=ExaoneIntentClassifierGateway(model=_EXAONE_MODEL),
        sommelier=get_sommelier_use_case(),
        langchain_chatbot=GeminiLangchainChatbotGateway(),
    )
