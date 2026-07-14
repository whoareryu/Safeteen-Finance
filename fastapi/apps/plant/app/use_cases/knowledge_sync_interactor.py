from __future__ import annotations

import asyncio

from ontology.app.dtos.sommelier_dto import GraphQueryDto
from ontology.app.ports.input.sommelier_graph_use_case import SommelierUseCase

from plant.app.dtos.knowledge_sync_dto import KnowledgeSyncResult, PlantKnowledgeFact
from plant.app.ports.input.knowledge_sync_use_case import KnowledgeSyncUseCase
from plant.app.ports.output.plant_knowledge_source_port import PlantKnowledgeSourcePort


def _build_merge_query(fact: PlantKnowledgeFact) -> GraphQueryDto:
    props = {key: value for key, value in fact.attributes.items() if value}
    set_clause = ", ".join(f"s.{key} = ${key}" for key in props)
    cypher = "MERGE (s:Species {name: $name})"
    if set_clause:
        cypher += f" SET {set_clause}"
    return GraphQueryDto(cypher=cypher, params={"name": fact.species_name, **props})


class KnowledgeSyncInteractor(KnowledgeSyncUseCase):

    def __init__(
        self,
        sources: list[PlantKnowledgeSourcePort],
        sommelier: SommelierUseCase,
    ) -> None:
        self._sources = sources
        self._sommelier = sommelier

    async def sync(self) -> KnowledgeSyncResult:
        facts: list[PlantKnowledgeFact] = []
        touched_sources: set[str] = set()
        for source in self._sources:
            source_facts = await asyncio.to_thread(source.fetch_all)
            facts.extend(source_facts)

        for fact in facts:
            await self._sommelier.query(_build_merge_query(fact))
            touched_sources.add(fact.source_api)

        return KnowledgeSyncResult(
            species_upserted=len(facts),
            sources=sorted(touched_sources),
        )
