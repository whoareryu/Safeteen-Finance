from ontology.app.dtos.sommelier_dto import GraphQueryDto, GraphResultDto
from ontology.app.ports.input.sommelier_graph_use_case import SommelierUseCase
from ontology.app.ports.output.sommelier_graph_port import SommelierPort


class SommelierInteractor(SommelierUseCase):
    def __init__(self, repo: SommelierPort) -> None:
        self._repo = repo

    async def query(self, dto: GraphQueryDto) -> GraphResultDto:
        records = await self._repo.run_cypher(dto.cypher, dto.params)
        return GraphResultDto(records=records)
