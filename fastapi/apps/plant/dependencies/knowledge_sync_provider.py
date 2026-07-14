from __future__ import annotations

from ontology.dependencies.sommelier_graph_provider import get_sommelier_use_case

from plant.adapter.outbound.http.air_purifying_plant_client import AirPurifyingPlantClient
from plant.adapter.outbound.http.drought_resistant_plant_client import (
    DroughtResistantPlantClient,
)
from plant.adapter.outbound.http.indoor_garden_plant_client import IndoorGardenPlantClient
from plant.app.ports.input.knowledge_sync_use_case import KnowledgeSyncUseCase
from plant.app.use_cases.knowledge_sync_interactor import KnowledgeSyncInteractor


def get_knowledge_sync_use_case() -> KnowledgeSyncUseCase:
    return KnowledgeSyncInteractor(
        sources=[
            AirPurifyingPlantClient(),
            DroughtResistantPlantClient(),
            IndoorGardenPlantClient(),
        ],
        sommelier=get_sommelier_use_case(),
    )
