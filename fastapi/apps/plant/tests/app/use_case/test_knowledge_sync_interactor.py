from __future__ import annotations

from ontology.app.dtos.sommelier_dto import GraphResultDto

from plant.app.dtos.knowledge_sync_dto import PlantKnowledgeFact
from plant.app.use_cases.knowledge_sync_interactor import KnowledgeSyncInteractor


class _FakeSource:
    def __init__(self, facts: list[PlantKnowledgeFact]) -> None:
        self._facts = facts

    def fetch_all(self) -> list[PlantKnowledgeFact]:
        return self._facts


class _RecordingSommelierUseCase:
    def __init__(self) -> None:
        self.queries: list = []

    async def query(self, dto):
        self.queries.append(dto)
        return GraphResultDto(records=[])


async def test_sync_upserts_a_species_node_per_fact_with_non_empty_attributes():
    sommelier = _RecordingSommelierUseCase()
    interactor = KnowledgeSyncInteractor(
        sources=[
            _FakeSource(
                [
                    PlantKnowledgeFact(
                        species_name="페페로미아 그라베올렌스",
                        source_api="drought_resistant",
                        attributes={"waterCycleInfo": "흙이 마르면 흠뻑 관수", "pestInfo": ""},
                    )
                ]
            ),
            _FakeSource(
                [
                    PlantKnowledgeFact(
                        species_name="가울테리아",
                        source_api="indoor_garden",
                        attributes={"idealHumidity": "40 ~ 70%"},
                    )
                ]
            ),
        ],
        sommelier=sommelier,
    )

    result = await interactor.sync()

    assert result.species_upserted == 2
    assert result.sources == ["drought_resistant", "indoor_garden"]
    assert len(sommelier.queries) == 2

    first = sommelier.queries[0]
    assert "MERGE (s:Species {name: $name})" in first.cypher
    assert "s.waterCycleInfo = $waterCycleInfo" in first.cypher
    assert "pestInfo" not in first.cypher  # empty-string attribute must be dropped
    assert first.params == {
        "name": "페페로미아 그라베올렌스",
        "waterCycleInfo": "흙이 마르면 흠뻑 관수",
    }


async def test_sync_with_no_facts_upserts_nothing():
    sommelier = _RecordingSommelierUseCase()
    interactor = KnowledgeSyncInteractor(sources=[_FakeSource([])], sommelier=sommelier)

    result = await interactor.sync()

    assert result.species_upserted == 0
    assert result.sources == []
    assert sommelier.queries == []
