from ontology.app.dtos.lens_dto import LensQueryDto, LensResultDto
from ontology.app.ports.input.lens_search_use_case import LensUseCase
from ontology.app.ports.output.lens_search_port import LensPort


class LensInteractor(LensUseCase):
    def __init__(self, repo: LensPort) -> None:
        self._repo = repo

    async def search(self, dto: LensQueryDto) -> LensResultDto:
        vector = await self._repo.embed(dto.query)
        hits = await self._repo.search_by_vector(dto.collection, vector, dto.limit)
        return LensResultDto(hits=hits)
