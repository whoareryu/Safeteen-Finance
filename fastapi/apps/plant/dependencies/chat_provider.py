from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.database import get_db
from ontology.dependencies.sommelier_graph_provider import get_sommelier_use_case

from plant.adapter.outbound.llm.plant_embedding_adapter import PlantEmbeddingAdapter
from plant.adapter.outbound.llm.plant_llm_adapter import PlantLlmAdapter
from plant.adapter.outbound.pg.plant_knowledge_pg_repository import PlantKnowledgePgRepository
from plant.app.ports.input.chat_use_case import ChatUseCase
from plant.app.use_cases.chat_interactor import ChatInteractor

_LLM = PlantLlmAdapter(model="exaone3.5:2.4b")
_EMBEDDING = PlantEmbeddingAdapter()


def get_chat_use_case(db: AsyncSession = Depends(get_db)) -> ChatUseCase:
    return ChatInteractor(
        knowledge_repository=PlantKnowledgePgRepository(session=db),
        embedding=_EMBEDDING,
        llm=_LLM,
        sommelier=get_sommelier_use_case(),
    )
