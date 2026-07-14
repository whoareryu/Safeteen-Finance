from __future__ import annotations

import logging

from ontology.app.dtos.sommelier_dto import GraphQueryDto
from ontology.app.ports.input.sommelier_graph_use_case import SommelierUseCase

from plant.app.dtos.chat_dto import ChatCommand, ChatResult
from plant.app.ports.input.chat_use_case import ChatUseCase
from plant.app.ports.output.embedding_port import EmbeddingPort
from plant.app.ports.output.llm_port import LlmPort
from plant.app.ports.output.plant_knowledge_repository import PlantKnowledgeRepository

logger = logging.getLogger(__name__)

_BASE_SYSTEM = (
    "당신은 반려식물을 돌보는 사용자를 돕는 다정한 식물 전문가입니다. 한국어로 답하세요."
)
_RAG_TOP_K = 3
_GROUNDED_TEMPERATURE = 0.2  # RAG 사실을 지어내지 않고 그대로 인용하도록 낮은 온도 사용


class ChatInteractor(ChatUseCase):

    def __init__(
        self,
        knowledge_repository: PlantKnowledgeRepository,
        embedding: EmbeddingPort,
        llm: LlmPort,
        sommelier: SommelierUseCase,
        llm_model_name: str = "exaone3.5:2.4b",
    ) -> None:
        self._knowledge_repository = knowledge_repository
        self._embedding = embedding
        self._llm = llm
        self._sommelier = sommelier
        self._llm_model_name = llm_model_name

    async def chat(self, command: ChatCommand) -> ChatResult:
        query = command.messages[-1].content
        logger.info("[plant-chat] 1/5 질문 수신: %r", query[:200])

        query_embedding = await self._embedding.embed(query)
        logger.info("[plant-chat] 2/5 쿼리 임베딩 생성 완료 (dim=%d)", len(query_embedding))

        matches = await self._knowledge_repository.find_similar(query_embedding, limit=_RAG_TOP_K)
        logger.info(
            "[plant-chat] 3/5 RAG 검색(plant_knowledge) 완료 — %s",
            [m.name for m in matches],
        )

        graph_fact = await self._query_ontology_hub(query)
        logger.info(
            "[plant-chat] 4/5 온톨로지 허브(Neo4j) 조회 완료 — %s",
            "찾음" if graph_fact else "없음",
        )

        system = self._build_system(matches, graph_fact)
        messages = [{"role": "system", "content": system}] + [
            {"role": m.role, "content": m.content} for m in command.messages
        ]
        temperature = _GROUNDED_TEMPERATURE if matches else None
        reply = await self._llm.chat(messages, temperature=temperature)
        logger.info(
            "[plant-chat] 5/5 LLM 응답 완료 (model=%s, len=%d)",
            self._llm_model_name,
            len(reply),
        )

        return ChatResult(text=reply.strip(), model=self._llm_model_name)

    async def _query_ontology_hub(self, query: str) -> str | None:
        try:
            graph = await self._sommelier.query(
                GraphQueryDto(
                    cypher=(
                        "MATCH (s:Species) "
                        "WHERE toLower($query) CONTAINS toLower(s.name) "
                        "RETURN s LIMIT 1"
                    ),
                    params={"query": query},
                )
            )
            return graph.records[0].get("s") if graph.records else None
        except Exception:
            logger.warning("[plant-chat] 온톨로지 허브 조회 실패 — 그래프 사실 없이 진행")
            return None

    def _build_system(self, matches: list, graph_fact: str | None) -> str:
        parts = [_BASE_SYSTEM]
        if matches:
            knowledge_text = "\n".join(f"- {m.name}: {m.description}" for m in matches)
            parts.append(
                "\n[검색된 참고 지식]\n"
                f"{knowledge_text}\n"
                "위 참고 지식에 질문과 관련된 항목이 있다면, 반드시 그 설명(색깔·증상·관리법 등 구체적 사실)을 "
                "그대로 인용해서 답변에 반영하세요. 참고 지식과 다른 내용을 지어내지 마세요. "
                "참고 지식에 관련 항목이 없을 때만 일반 지식으로 답하세요."
            )
        if graph_fact:
            parts.append(f"\n[온톨로지 참고 사실]\n{graph_fact}")
        return "\n".join(parts)
