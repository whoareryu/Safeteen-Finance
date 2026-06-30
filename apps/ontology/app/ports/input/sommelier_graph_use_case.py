from abc import ABC, abstractmethod

from ontology.app.dtos.sommelier_dto import GraphQueryDto, GraphResultDto


class SommelierUseCase(ABC):
    @abstractmethod
    async def query(self, dto: GraphQueryDto) -> GraphResultDto: ...
