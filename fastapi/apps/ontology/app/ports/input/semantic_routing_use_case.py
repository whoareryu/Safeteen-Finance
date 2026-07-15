from abc import ABC, abstractmethod

from ontology.app.dtos.semantic_routing_dto import (
    SemanticRoutingQueryDto,
    SemanticRoutingResultDto,
)


class SemanticRoutingUseCase(ABC):
    @abstractmethod
    async def route(self, dto: SemanticRoutingQueryDto) -> SemanticRoutingResultDto: ...
