from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from star_craft.app.dtos.kerrigan_topology_dto import SpokeInfo, TopologyQuery, TopologyResponse
from star_craft.app.ports.output.kerrigan_topology_port import KerriganTopologyPort

_STATIC_SPOKES = (
    SpokeInfo(name="titanic", prefix="/api/titanic", status="active"),
    SpokeInfo(name="restaurant", prefix="/api/restaurant", status="active"),
    SpokeInfo(name="silicon_valley", prefix="/api/silicon-valley", status="active"),
    SpokeInfo(name="user", prefix="/api/user", status="active"),
)


class KerriganTopologyRepository(KerriganTopologyPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_spokes(self, query: TopologyQuery) -> TopologyResponse:
        return TopologyResponse(spokes=_STATIC_SPOKES, total=len(_STATIC_SPOKES))
