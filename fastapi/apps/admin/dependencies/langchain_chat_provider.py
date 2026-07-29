from __future__ import annotations

from fastapi import Depends

from admin.adapter.outbound.client.ontology_semantic_routing_chat_client import (
    OntologySemanticRoutingChatClient,
)
from admin.app.ports.input.langchain_chat_use_case import LangchainChatUseCase
from admin.app.use_cases.langchain_chat_interactor import LangchainChatInteractor
from ontology.app.ports.input.semantic_routing_use_case import SemanticRoutingUseCase
from ontology.dependencies.semantic_routing_provider import get_semantic_routing_use_case


def get_langchain_chat_use_case(
    semantic_routing: SemanticRoutingUseCase = Depends(get_semantic_routing_use_case),
) -> LangchainChatUseCase:
    return LangchainChatInteractor(generator=OntologySemanticRoutingChatClient(semantic_routing))
