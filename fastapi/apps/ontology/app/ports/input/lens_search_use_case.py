from abc import ABC, abstractmethod

from ontology.app.dtos.lens_dto import LensQueryDto, LensResultDto


class LensUseCase(ABC):
    @abstractmethod
    async def search(self, dto: LensQueryDto) -> LensResultDto: ...
