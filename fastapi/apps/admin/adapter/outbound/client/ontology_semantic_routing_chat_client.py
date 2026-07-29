from __future__ import annotations

from admin.app.ports.output.langchain_chat_generator_port import LangchainChatGeneratorPort
from ontology.app.dtos.semantic_routing_dto import SemanticRoutingQueryDto
from ontology.app.ports.input.semantic_routing_use_case import SemanticRoutingUseCase


class OntologySemanticRoutingChatClient(LangchainChatGeneratorPort):
    """ontology 허브의 시멘틱 라우터(SemanticRoutingUseCase)를 거쳐 응답을 받는 어댑터."""

    def __init__(self, semantic_routing: SemanticRoutingUseCase) -> None:
        self._semantic_routing = semantic_routing

    async def reply(self, message: str) -> str:
        result = await self._semantic_routing.route(SemanticRoutingQueryDto(question=message))
        return result.answer
