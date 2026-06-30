from abc import ABC, abstractmethod

from ontology.app.dtos.maestro_dto import MaestroQueryDto, MaestroResultDto
from ontology.app.dtos.dispatch_dto import DispatchRequestDto, DispatchResultDto


class MaestroUseCase(ABC):
    @abstractmethod
    async def route(self, dto: MaestroQueryDto) -> MaestroResultDto: ...

    @abstractmethod
    async def dispatch(self, dto: DispatchRequestDto) -> DispatchResultDto: ...
