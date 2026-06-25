from __future__ import annotations

from star_craft.app.dtos.kerrigan_topology_dto import SpokeInfo, TopologyQuery, TopologyResponse
from star_craft.app.ports.input.kerrigan_topology_use_case import KerriganTopologyUseCase
from star_craft.app.ports.output.kerrigan_topology_port import KerriganTopologyPort

_REGISTERED_SPOKES = (
    SpokeInfo(name="titanic", prefix="/api/titanic", status="active"),
    SpokeInfo(name="restaurant", prefix="/api/restaurant", status="active"),
    SpokeInfo(name="silicon_valley", prefix="/api/silicon-valley", status="active"),
    SpokeInfo(name="user", prefix="/api/user", status="active"),
)


class KerriganTopologyInteractor(KerriganTopologyUseCase):
    """Sarah Kerrigan — 허브 토폴로지 레지스트리. 등록된 스포크 목록을 반환한다."""

    def __init__(self, repository: KerriganTopologyPort) -> None:
        self._repository = repository

    async def list_spokes(self, query: TopologyQuery) -> TopologyResponse:
        spokes = await self._repository.list_spokes(query)
        if query.spoke_name:
            spokes = TopologyResponse(
                spokes=tuple(s for s in spokes.spokes if s.name == query.spoke_name),
                total=0,
            )
            return TopologyResponse(spokes=spokes.spokes, total=len(spokes.spokes))
        return spokes
