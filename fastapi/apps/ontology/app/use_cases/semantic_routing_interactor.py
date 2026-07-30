from __future__ import annotations

import json

from ontology.app.dtos.semantic_routing_dto import (
    SemanticRoutingQueryDto,
    SemanticRoutingResultDto,
)
from ontology.app.dtos.sommelier_dto import GraphQueryDto
from ontology.app.ports.input.semantic_routing_use_case import SemanticRoutingUseCase
from ontology.app.ports.input.sommelier_graph_use_case import SommelierUseCase
from ontology.app.ports.output.intent_classification_gateway import IntentClassificationGateway
from ontology.app.ports.output.langchain_chatbot_gateway import LangchainChatbotGateway
from ontology.app.ports.output.plant_knowledge_search_port import PlantKnowledgeSearchPort
from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator

_GRAPH_SIGNALS = ["관계", "연결", "이웃", "경로", "링크"]

_RAG_PROMPT_TEMPLATE = """너는 사내 온톨로지 지식에만 기반하여 사실을 전달하는 AI 비서야.
반드시 제공된 [Context] 내의 정보만 사실에 입각해서 정직하게 답변해줘.
[Context]에 없는 내용을 추측하거나 외부 지식으로 보완해서 지어내는 것은 절대 허용되지 않아.

[Context]
{context}
"""


class SemanticRoutingInteractor(SemanticRoutingUseCase):
    def __init__(
        self,
        llm: T1MidFakerOrchestrator,
        intent_gateway: IntentClassificationGateway,
        sommelier: SommelierUseCase,
        plant_knowledge: PlantKnowledgeSearchPort,
        langchain_chatbot: LangchainChatbotGateway,
    ) -> None:
        self._llm = llm
        self._intent_gateway = intent_gateway
        self._sommelier = sommelier
        self._plant_knowledge = plant_knowledge
        self._langchain_chatbot = langchain_chatbot

    async def route(self, dto: SemanticRoutingQueryDto) -> SemanticRoutingResultDto:
        intent = await self._intent_gateway.classify(dto.question)
        destination, entities = intent.destination, intent.entities

        if destination == "crud":
            answer = f"[CRUD 실행] {', '.join(entities)} 관련 DB 조작을 감지하여 안전하게 수행합니다."
            return SemanticRoutingResultDto(answer=answer, destination=destination, entities=entities)

        if destination == "gemini":
            answer = await self._langchain_chatbot.chat(dto.question)
            return SemanticRoutingResultDto(answer=answer, destination=destination, entities=entities)

        answer = await self._answer_with_ontology(dto.question, entities)
        return SemanticRoutingResultDto(answer=answer, destination="exaone_rag", entities=entities)

    async def _answer_with_ontology(self, question: str, entities: list[str]) -> str:
        context = await self._search_ontology(question, entities)
        if not context:
            return f"죄송합니다. 입력하신 키워드({', '.join(entities)}) 관련 정보를 온톨로지 DB에서 찾을 수 없습니다."

        rag_prompt = _RAG_PROMPT_TEMPLATE.format(context=json.dumps(context, ensure_ascii=False))
        return await self._llm.chat([
            {"role": "system", "content": rag_prompt},
            {"role": "user", "content": question},
        ])

    async def _search_ontology(self, question: str, entities: list[str]) -> list[dict]:
        keyword = " ".join(entities) or question
        if any(sig in question for sig in _GRAPH_SIGNALS):
            cypher = "MATCH (n) WHERE n.name CONTAINS $keyword RETURN n LIMIT 5"
            result = await self._sommelier.query(GraphQueryDto(cypher=cypher, params={"keyword": keyword[:20]}))
            return result.records

        return await self._plant_knowledge.search(keyword)
